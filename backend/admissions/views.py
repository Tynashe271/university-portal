from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import AdmissionApplication, MeritList
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
        # look up a single application by its reference number (applicant
        # status portal). Listing every application and reviewing decisions
        # is restricted to admissions staff.
        if self.action in ('create', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsAdmissionsAdmin()]

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
        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_date = timezone.now()
        application.save()
        return Response({'status': 'approved'})

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
