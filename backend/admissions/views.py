from django.contrib.auth.hashers import check_password
from django.http import Http404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from admins.utils import log_action
from .classing import MAX_POINTS, MIN_POINTS, assign_class
from .emails import send_application_confirmation_email
from .models import AdmissionApplication, MeritList
from .pdf import generate_acceptance_letter
from .serializers import AdmissionApplicationSerializer, MeritListSerializer


class IsAdmissionsAdmin(permissions.BasePermission):
    """Only authenticated admin-role users may list/review applications."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin_user()
        )


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdmissionApplication.objects.all()
    serializer_class = AdmissionApplicationSerializer
    lookup_field = 'application_number'
    lookup_value_regex = '[^/]+'

    def get_permissions(self):
        # Anyone can submit a new application (public admissions form) or
        # sign in to the applicant portal with their reference number and
        # portal password. Reading an application directly by reference
        # (without the password), listing every application, and reviewing
        # decisions is restricted to admissions staff.
        if self.action in ('create', 'login'):
            return [permissions.AllowAny()]
        return [IsAdmissionsAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        email_sent = send_application_confirmation_email(application)
        data = dict(serializer.data)
        data['email_sent'] = email_sent
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def login(self, request, application_number=None):
        try:
            application = self.get_object()
        except Http404:
            application = None
        password = request.data.get('password', '')
        if not application or not application.portal_password or not check_password(password, application.portal_password):
            return Response({'error': 'Application reference or password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(AdmissionApplicationSerializer(application, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, application_number=None):
        application = self.get_object()
        application.status = 'submitted'
        application.submitted_date = timezone.now()
        application.save()
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['post'])
    def approve(self, request, application_number=None):
        application = self.get_object()

        # Form 1 has a defined points -> class scheme; other grades are
        # placed manually, so points/class placement is skipped for them.
        points = None
        if application.grade_applying_for == 'form1':
            raw_points = request.data.get('points')
            if raw_points in (None, ''):
                return Response(
                    {'error': "Enter the applicant's points to place them in a class before accepting."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                points = int(raw_points)
            except (TypeError, ValueError):
                return Response({'error': 'Points must be a whole number.'}, status=status.HTTP_400_BAD_REQUEST)

            class_name, outcome = assign_class(application, points)

            if outcome == 'out_of_range':
                return Response(
                    {'error': f'Points must be between {MIN_POINTS} and {MAX_POINTS} to place this applicant in a class.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if outcome == 'full':
                # Every stream for this grade/year is at capacity — there is
                # nowhere left to place the student, so the acceptance is
                # automatically turned into a decline instead.
                application.points = points
                application.assigned_class = ''
                application.status = 'rejected'
                application.reviewed_by = request.user
                application.reviewed_date = timezone.now()
                note = f"Automatically declined: every Form 1 class from the applicant's points band ({points} points) upward is already full."
                application.additional_notes = f"{application.additional_notes}\n{note}".strip()
                application.save()
                log_action(request.user, 'update', 'AdmissionApplication', application.id,
                           f"Auto-declined {application.application_number}: {note}", request)
                return Response({
                    'status': 'rejected',
                    'reason': 'All classes for this grade are already full.',
                })

            application.points = points
            application.assigned_class = class_name

        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_date = timezone.now()
        application.save()
        # Generate the PDF acceptance letter so it's ready to download from
        # the applicant portal as soon as the applicant checks their status.
        letter_generated = generate_acceptance_letter(application)
        log_action(request.user, 'update', 'AdmissionApplication', application.id,
                   f"Approved {application.application_number}" + (f" into class {application.assigned_class}" if application.assigned_class else ""), request)
        return Response({
            'status': 'approved',
            'assigned_class': application.assigned_class or None,
            'acceptance_letter_generated': letter_generated,
        })

    @action(detail=True, methods=['post'])
    def convert_to_student(self, request, application_number=None):
        """Turn an accepted application into a real student account —
        closes the Admissions -> Student Record step. Best-effort links the
        new account to a pre-defined academics.Classroom matching the
        assigned_class string (e.g. "1-2"); leaves it unset if none exists
        yet, since Classroom records are optional/admin-defined."""
        application = self.get_object()
        if application.status not in ('approved', 'admitted', 'enrolled'):
            return Response(
                {'error': 'Only an accepted application can be converted into a student account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hasattr(application, 'student_account') and application.student_account:
            return Response(
                {'error': 'This application already has a student account.', 'username': application.student_account.username},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils.crypto import get_random_string
        from academics.models import Classroom
        from students.models import User

        name_parts = application.student_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        year = timezone.now().year
        count = User.objects.filter(role='student', enrollment_date__year=year).count() + 1
        student_id = f"STU{year}{count:04d}"
        raw_password = get_random_string(10)

        classroom = None
        if application.assigned_class:
            try:
                stream = int(application.assigned_class.split('-')[-1])
                classroom = Classroom.objects.filter(
                    grade=application.grade_applying_for,
                    stream=stream,
                    academic_year=application.academic_year,
                ).first()
            except (ValueError, IndexError):
                classroom = None

        user = User.objects.create_user(
            username=student_id.lower(),
            password=raw_password,
            first_name=first_name,
            last_name=last_name,
            email=application.parent_email,
            role='student',
            student_id=student_id,
            date_of_birth=application.date_of_birth,
            address=application.parent_address,
            previous_school=application.previous_school,
            previous_grade=application.previous_grade,
            emergency_contact_name=application.parent_name,
            emergency_contact_phone=application.parent_phone,
            emergency_contact_relationship='Parent/Guardian',
            classroom=classroom,
            admission_application=application,
        )
        application.status = 'enrolled'
        application.save()
        log_action(request.user, 'create', 'User', user.id,
                   f"Converted {application.application_number} into student account {user.username}", request)

        return Response({
            'username': user.username,
            'student_id': user.student_id,
            'temporary_password': raw_password,
            'classroom': classroom.name if classroom else None,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reject(self, request, application_number=None):
        application = self.get_object()
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_date = timezone.now()
        application.save()
        log_action(request.user, 'update', 'AdmissionApplication', application.id,
                   f"Rejected {application.application_number}", request)
        return Response({'status': 'rejected'})


class MeritListViewSet(viewsets.ModelViewSet):
    queryset = MeritList.objects.all()
    serializer_class = MeritListSerializer
