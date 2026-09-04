from django.urls import path
from .views import (
    TimeSlotListCreateView, TimeSlotDetailView,
    ScheduleListCreateView, ScheduleDetailView,
    TimetableListView, generate_timetable, user_schedule,
    detect_conflicts, resolve_conflict
)

urlpatterns = [
    # Time Slots
    path('time-slots/', TimeSlotListCreateView.as_view(), name='time-slot-list'),
    path('time-slots/<int:pk>/', TimeSlotDetailView.as_view(), name='time-slot-detail'),
    
    # Schedules
    path('schedules/', ScheduleListCreateView.as_view(), name='schedule-list'),
    path('schedules/<int:pk>/', ScheduleDetailView.as_view(), name='schedule-detail'),
    
    # Timetables
    path('timetables/', TimetableListView.as_view(), name='timetable-list'),
    path('timetables/generate/', generate_timetable, name='generate-timetable'),
    path('user-schedule/', user_schedule, name='user-schedule'),
    
    # Conflicts
    path('conflicts/', detect_conflicts, name='detect-conflicts'),
    path('conflicts/<int:conflict_id>/resolve/', resolve_conflict, name='resolve-conflict'),
]