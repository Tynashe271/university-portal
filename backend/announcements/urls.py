from django.urls import path
from .views import (
    AnnouncementListCreateView, AnnouncementDetailView,
    mark_as_read, user_announcements, announcement_stats
)

urlpatterns = [
    # Announcements
    path('', AnnouncementListCreateView.as_view(), name='announcement-list'),
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('<int:announcement_id>/read/', mark_as_read, name='mark-read'),
    path('user/', user_announcements, name='user-announcements'),
    path('stats/', announcement_stats, name='announcement-stats'),
]