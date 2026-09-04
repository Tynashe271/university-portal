from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Assignment, AssignmentSubmission, AssignmentAttachment
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer, AssignmentAttachmentSerializer
from courses.models import Course, Enrollment
from students.models import User

class AssignmentListCreateView(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        status_filter = self.request.query_params.get('status', 'published')
        
        queryset = Assignment.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False)
        
        if user.is_student():
            # Students can only see assignments for courses they're enrolled in
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled'
            ).values_list('course_id', flat=True)
            return queryset.filter(course_id__in=enrolled_courses)
        elif user.is_admin_user():
            # Instructors can see assignments for courses they teach
            return queryset.filter(course__instructor=user)
        return Assignment.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(created_by=user)
        else:
            raise PermissionError("Only instructors can create assignments")

class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled'
            ).values_list('course_id', flat=True)
            return Assignment.objects.filter(course_id__in=enrolled_courses, is_published=True)
        elif user.is_admin_user():
            return Assignment.objects.filter(course__instructor=user)
        return Assignment.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only instructors can update assignments")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only instructors can delete assignments")

class AssignmentSubmissionListCreateView(generics.ListCreateAPIView):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        assignment_id = self.request.query_params.get('assignment', None)
        
        queryset = AssignmentSubmission.objects.all()
        
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        
        if user.is_student():
            return queryset.filter(student=user)
        elif user.is_admin_user():
            # Instructors can see submissions for their courses
            return queryset.filter(assignment__course__instructor=user)
        return AssignmentSubmission.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        assignment_id = self.request.data.get('assignment')
        
        try:
            assignment = Assignment.objects.get(id=assignment_id)
            
            if user.is_student():
                # Check if student is enrolled in the course
                enrollment = Enrollment.objects.get(
                    student=user,
                    course=assignment.course,
                    status='enrolled'
                )
                
                # Check if assignment is overdue
                is_late = timezone.now() > assignment.due_date
                
                submission = serializer.save(
                    student=user,
                    enrollment=enrollment,
                    is_late=is_late,
                    status='submitted' if not is_late else 'late'
                )
                return submission
            else:
                raise PermissionError("Only students can submit assignments")
                
        except Assignment.DoesNotExist:
            raise ValueError("Assignment not found")
        except Enrollment.DoesNotExist:
            raise ValueError("Student not enrolled in this course")

class AssignmentSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            return AssignmentSubmission.objects.filter(student=user)
        elif user.is_admin_user():
            return AssignmentSubmission.objects.filter(assignment__course__instructor=user)
        return AssignmentSubmission.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        submission = self.get_object()
        
        if user.is_student():
            # Students can only update their own submissions if not graded
            if submission.status not in ['graded', 'returned']:
                serializer.save()
            else:
                raise PermissionError("Cannot update graded submissions")
        elif user.is_admin_user():
            # Instructors can grade submissions
            if 'grade' in self.request.data or 'feedback' in self.request.data:
                serializer.save(graded_by=user, graded_at=timezone.now(), status='graded')
            else:
                serializer.save()
        else:
            raise PermissionError("Permission denied")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_student() and instance.student == user:
            if instance.status not in ['graded', 'returned']:
                instance.delete()
            else:
                raise PermissionError("Cannot delete graded submissions")
        elif user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Permission denied")

class AssignmentAttachmentListCreateView(generics.ListCreateAPIView):
    queryset = AssignmentAttachment.objects.all()
    serializer_class = AssignmentAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        assignment_id = self.request.query_params.get('assignment', None)
        
        queryset = AssignmentAttachment.objects.all()
        
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        
        if user.is_student():
            # Students can see attachments for assignments in their enrolled courses
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled'
            ).values_list('course_id', flat=True)
            return queryset.filter(assignment__course_id__in=enrolled_courses)
        elif user.is_admin_user():
            return queryset.filter(assignment__course__instructor=user)
        return AssignmentAttachment.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(uploaded_by=user)
        else:
            raise PermissionError("Only instructors can upload attachments")

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_assignments(request):
    user = request.user
    
    if not user.is_student():
        return Response({'error': 'Student access required'}, status=status.HTTP_403_FORBIDDEN)
    
    enrolled_courses = Enrollment.objects.filter(
        student=user,
        status='enrolled'
    )
    
    assignments = []
    for enrollment in enrolled_courses:
        course_assignments = Assignment.objects.filter(
            course=enrollment.course,
            is_published=True
        )
        
        for assignment in course_assignments:
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=user
            ).first()
            
            assignment_data = AssignmentSerializer(assignment).data
            assignment_data['submission_status'] = submission.status if submission else 'not_submitted'
            assignment_data['submission_id'] = submission.id if submission else None
            assignment_data['grade'] = submission.grade if submission else None
            
            assignments.append(assignment_data)
    
    return Response({
        'student': user.username,
        'assignments': assignments
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def instructor_assignments(request):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Instructor access required'}, status=status.HTTP_403_FORBIDDEN)
    
    assignments = Assignment.objects.filter(course__instructor=user)
    serializer = AssignmentSerializer(assignments, many=True)
    
    return Response({
        'instructor': user.username,
        'assignments': serializer.data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def grade_submission(request, submission_id):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Instructor access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        submission = AssignmentSubmission.objects.get(id=submission_id)
        
        # Check if instructor teaches the course
        if submission.assignment.course.instructor != user:
            return Response({'error': 'Not authorized to grade this submission'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        grade = request.data.get('grade')
        feedback = request.data.get('feedback', '')
        
        submission.grade = grade
        submission.feedback = feedback
        submission.graded_by = user
        submission.graded_at = timezone.now()
        submission.status = 'graded'
        submission.save()
        
        return Response(AssignmentSubmissionSerializer(submission).data)
        
    except AssignmentSubmission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
