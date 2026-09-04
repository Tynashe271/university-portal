from django.urls import path
from .views import AdminPermissionListCreateView, AdminPermissionDetailView, grant_permission, SystemLogListView

urlpatterns = [
    path('permissions/', AdminPermissionListCreateView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', AdminPermissionDetailView.as_view(), name='permission-detail'),
    path('permissions/grant/', grant_permission, name='grant-permission'),
    path('logs/', SystemLogListView.as_view(), name='system-logs'),
]