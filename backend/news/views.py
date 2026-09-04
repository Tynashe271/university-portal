from rest_framework import permissions, viewsets
from .models import NewsEvent
from .serializers import NewsEventSerializer


class IsSchoolAdmin(permissions.BasePermission):
    """Only authenticated admin-role users may create/edit/delete posts."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin_user()
        )


class NewsEventViewSet(viewsets.ModelViewSet):
    queryset = NewsEvent.objects.all()
    serializer_class = NewsEventSerializer

    def get_permissions(self):
        # The school website (visitors, no login) reads news and events
        # publicly. Only admissions/school staff can add or remove posts.
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [IsSchoolAdmin()]

    def get_queryset(self):
        queryset = NewsEvent.objects.all()
        user = self.request.user
        # Non-admin visitors (including anonymous website visitors) only
        # ever see published posts; staff can see drafts too when managing.
        if not (user and user.is_authenticated and user.is_admin_user()):
            queryset = queryset.filter(published=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user if user.is_authenticated else None)
