from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsAdminUser
from .models import Message, ConferenceSchedule, ParentProfile, StudentParentRelation
from .serializers import (
    MessageSerializer, ConferenceScheduleSerializer,
    ParentProfileSerializer, StudentParentRelationSerializer,
)


class MessageViewSet(viewsets.ModelViewSet):
    """A message is private between its sender and recipient — previously
    anyone authenticated could list/read every message in the system."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return Message.objects.all()
        return Message.objects.filter(Q(sender=user) | Q(recipient=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ConferenceScheduleViewSet(viewsets.ModelViewSet):
    queryset = ConferenceSchedule.objects.all()
    serializer_class = ConferenceScheduleSerializer


class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.select_related('user').all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def quick_add(self, request):
        """Create a parent/guardian login account, profile and a link to
        one student in a single call — mirrors admissions'
        convert_to_student for the same "don't make the admin fill in an
        enterprise HR form to add one person" reasoning."""
        full_name = (request.data.get('full_name') or '').strip()
        student_id = request.data.get('student')
        if not full_name or not student_id:
            return Response({'error': 'full_name and student are required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils.crypto import get_random_string
        from django.utils import timezone
        from students.models import User

        try:
            student = User.objects.get(pk=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        year = timezone.now().year
        count = User.objects.filter(role='parent', enrollment_date__year=year).count() + 1
        username = f"parent{year}{count:04d}"
        raw_password = get_random_string(10)

        parent_user = User.objects.create_user(
            username=username,
            password=raw_password,
            first_name=first_name,
            last_name=last_name,
            email=request.data.get('email', ''),
            phone=request.data.get('phone', ''),
            role='parent',
        )
        profile = ParentProfile.objects.create(
            user=parent_user,
            relationship=request.data.get('relationship', 'guardian'),
        )
        StudentParentRelation.objects.create(
            student=student,
            parent=parent_user,
            relationship=request.data.get('relationship', 'guardian'),
            is_primary_contact=True,
        )
        return Response({
            'username': parent_user.username,
            'temporary_password': raw_password,
            'profile': ParentProfileSerializer(profile).data,
        }, status=status.HTTP_201_CREATED)


class StudentParentRelationViewSet(viewsets.ModelViewSet):
    queryset = StudentParentRelation.objects.select_related('student', 'parent').all()
    serializer_class = StudentParentRelationSerializer
    permission_classes = [IsAdminUser]
