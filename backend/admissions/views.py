from django.contrib.auth.hashers import check_password
from django.http import Http404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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
        return Response({
            'status': 'approved',
            'assigned_class': application.assigned_class or None,
            'acceptance_letter_generated': letter_generated,
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, application_number=None):
        application = self.get_object()
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_date = timezone.now()
        application.save()
        return Response({'status': 'rejected'})


class MeritListViewSet(viewsets.ModelViewSet):
    queryset = MeritList.objects.all()
    serializer_class = MeritListSerializer
