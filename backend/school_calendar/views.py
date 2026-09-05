from rest_framework import permissions, viewsets
from config.permissions import IsAdminUser
from .models import CalendarEvent
from .serializers import CalendarEventSerializer


class CalendarEventViewSet(viewsets.ModelViewSet):
    """Anyone signed in (student, parent, staff, admin) can read the shared
    calendar; only admins can create, edit or remove events on it."""
    queryset = CalendarEvent.objects.select_related('term').all()
    serializer_class = CalendarEventSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        event_type = self.request.query_params.get('event_type')
        academic_year = self.request.query_params.get('academic_year')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
