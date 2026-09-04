from django.urls import path
from .views import (
    DepartmentListCreateView, DepartmentDetailView,
    CourseListCreateView, CourseDetailView,
    EnrollmentListCreateView, EnrollmentDetailView,
    GradeListCreateView, GradeDetailView,
    enroll_student, student_dashboard, admin_dashboard
)

urlpatterns = [
    # Departments
    path('departments/', DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    
    # Courses
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    
    # Enrollments
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('enroll/', enroll_student, name='enroll-student'),
    
    # Grades
    path('grades/', GradeListCreateView.as_view(), name='grade-list'),
    path('grades/<int:pk>/', GradeDetailView.as_view(), name='grade-detail'),
    
    # Dashboards
    path('dashboard/student/', student_dashboard, name='student-dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin-dashboard'),
]