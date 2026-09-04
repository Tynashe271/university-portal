from django.urls import path
from .views import (
    AssignmentListCreateView, AssignmentDetailView,
    AssignmentSubmissionListCreateView, AssignmentSubmissionDetailView,
    AssignmentAttachmentListCreateView,
    student_assignments, instructor_assignments, grade_submission
)

urlpatterns = [
    # Assignments
    path('', AssignmentListCreateView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    
    # Submissions
    path('submissions/', AssignmentSubmissionListCreateView.as_view(), name='submission-list'),
    path('submissions/<int:pk>/', AssignmentSubmissionDetailView.as_view(), name='submission-detail'),
    path('submissions/<int:submission_id>/grade/', grade_submission, name='grade-submission'),
    
    # Attachments
    path('attachments/', AssignmentAttachmentListCreateView.as_view(), name='attachment-list'),
    
    # Special endpoints
    path('student/', student_assignments, name='student-assignments'),
    path('instructor/', instructor_assignments, name='instructor-assignments'),
]