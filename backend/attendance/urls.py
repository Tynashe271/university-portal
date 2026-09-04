from django.urls import path
from .views import (
    AttendanceRecordListCreateView, AttendanceRecordDetailView,
    AttendanceSessionListCreateView, AttendanceSessionDetailView,
    AttendanceSummaryListView, bulk_mark_attendance,
    student_attendance_report, course_attendance_report
)

urlpatterns = [
    # Attendance Records
    path('records/', AttendanceRecordListCreateView.as_view(), name='attendance-record-list'),
    path('records/<int:pk>/', AttendanceRecordDetailView.as_view(), name='attendance-record-detail'),
    
    # Attendance Sessions
    path('sessions/', AttendanceSessionListCreateView.as_view(), name='attendance-session-list'),
    path('sessions/<int:pk>/', AttendanceSessionDetailView.as_view(), name='attendance-session-detail'),
    path('sessions/bulk-mark/', bulk_mark_attendance, name='bulk-mark-attendance'),
    
    # Attendance Summaries
    path('summaries/', AttendanceSummaryListView.as_view(), name='attendance-summary-list'),
    
    # Reports
    path('report/student/', student_attendance_report, name='student-attendance-report'),
    path('report/course/<int:course_id>/', course_attendance_report, name='course-attendance-report'),
]