from rest_framework import permissions, viewsets
from .models import StaffProfile
from .serializers import StaffProfileSerializer


class IsSchoolAdmin(permissions.BasePermission):
    """Staff records (teachers, SDC members, ...) are internal — only
    authenticated admin-role users may view or manage them."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin_user()
        )


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all().order_by('employee_type', 'full_name')
    serializer_class = StaffProfileSerializer
    permission_classes = [IsSchoolAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_type = self.request.query_params.get('employee_type')
        if employee_type:
            queryset = queryset.filter(employee_type=employee_type)
        return queryset
