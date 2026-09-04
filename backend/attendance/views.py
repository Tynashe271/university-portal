from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from .models import AttendanceRecord, AttendanceSession, AttendanceSummary
from .serializers import AttendanceRecordSerializer, AttendanceSessionSerializer, AttendanceSummarySerializer
from courses.models import Enrollment
from students.models import User

class AttendanceRecordListCreateView(generics.ListCreateAPIView):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        date = self.request.query_params.get('date', None)
        student_id = self.request.query_params.get('student', None)
        
        queryset = AttendanceRecord.objects.all()
        
        if course_id:
            queryset = queryset.filter(enrollment__course_id=course_id)
        if date:
            queryset = queryset.filter(date=date)
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        
        if user.is_student():
            return queryset.filter(enrollment__student=user)
        elif user.is_admin_user():
            return queryset
        return AttendanceRecord.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            record = serializer.save(marked_by=user)
            # Update attendance summary
            self.update_attendance_summary(record.enrollment)
        else:
            raise PermissionError("Only admins can mark attendance")
    
    def update_attendance_summary(self, enrollment):
        summary, created = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
        
        # Recalculate all attendance records for this enrollment
        records = AttendanceRecord.objects.filter(enrollment=enrollment)
        summary.total_classes = records.count()
        summary.present_count = records.filter(status='present').count()
        summary.absent_count = records.filter(status='absent').count()
        summary.late_count = records.filter(status='late').count()
        summary.excused_count = records.filter(status='excused').count()
        summary.calculate_percentage()

class AttendanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            return AttendanceRecord.objects.filter(enrollment__student=user)
        elif user.is_admin_user():
            return AttendanceRecord.objects.all()
        return AttendanceRecord.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            record = serializer.save()
            self.update_attendance_summary(record.enrollment)
        else:
            raise PermissionError("Only admins can update attendance")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            enrollment = instance.enrollment
            instance.delete()
            self.update_attendance_summary(enrollment)
        else:
            raise PermissionError("Only admins can delete attendance")
    
    def update_attendance_summary(self, enrollment):
        summary, created = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
        records = AttendanceRecord.objects.filter(enrollment=enrollment)
        summary.total_classes = records.count()
        summary.present_count = records.filter(status='present').count()
        summary.absent_count = records.filter(status='absent').count()
        summary.late_count = records.filter(status='late').count()
        summary.excused_count = records.filter(status='excused').count()
        summary.calculate_percentage()

class AttendanceSessionListCreateView(generics.ListCreateAPIView):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        
        queryset = AttendanceSession.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if user.is_student():
            # Students can only see sessions for courses they're enrolled in
            enrolled_courses = Enrollment.objects.filter(student=user, status='enrolled').values_list('course_id', flat=True)
            return queryset.filter(course_id__in=enrolled_courses)
        elif user.is_admin_user():
            return queryset
        return AttendanceSession.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save(created_by=user)
        else:
            raise PermissionError("Only admins can create attendance sessions")

class AttendanceSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only admins can update attendance sessions")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only admins can delete attendance sessions")

class AttendanceSummaryListView(generics.ListAPIView):
    queryset = AttendanceSummary.objects.all()
    serializer_class = AttendanceSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course', None)
        
        queryset = AttendanceSummary.objects.all()
        
        if course_id:
            queryset = queryset.filter(enrollment__course_id=course_id)
        
        if user.is_student():
            return queryset.filter(enrollment__student=user)
        elif user.is_admin_user():
            return queryset
        return AttendanceSummary.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_mark_attendance(request):
    user = request.user
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    session_id = request.data.get('session_id')
    attendance_data = request.data.get('attendance', [])  # List of {enrollment_id, status, notes}
    
    try:
        session = AttendanceSession.objects.get(id=session_id)
        
        created_records = []
        updated_records = []
        
        for data in attendance_data:
            enrollment_id = data.get('enrollment_id')
            status = data.get('status', 'present')
            notes = data.get('notes', '')
            
            enrollment = Enrollment.objects.get(id=enrollment_id)
            
            record, created = AttendanceRecord.objects.update_or_create(
                enrollment=enrollment,
                date=session.date,
                defaults={
                    'status': status,
                    'notes': notes,
                    'marked_by': user
                }
            )
            
            # Update attendance summary
            summary, _ = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
            records = AttendanceRecord.objects.filter(enrollment=enrollment)
            summary.total_classes = records.count()
            summary.present_count = records.filter(status='present').count()
            summary.absent_count = records.filter(status='absent').count()
            summary.late_count = records.filter(status='late').count()
            summary.excused_count = records.filter(status='excused').count()
            summary.calculate_percentage()
            
            if created:
                created_records.append(record)
            else:
                updated_records.append(record)
        
        return Response({
            'message': 'Attendance marked successfully',
            'created': len(created_records),
            'updated': len(updated_records)
        }, status=status.HTTP_200_OK)
        
    except AttendanceSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_attendance_report(request):
    user = request.user
    
    if not user.is_student():
        return Response({'error': 'Student access required'}, status=status.HTTP_403_FORBIDDEN)
    
    enrollments = Enrollment.objects.filter(student=user, status='enrolled')
    summaries = []
    
    for enrollment in enrollments:
        summary, created = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
        summaries.append(AttendanceSummarySerializer(summary).data)
    
    return Response({
        'student': user.username,
        'attendance_summaries': summaries
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_attendance_report(request, course_id):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from courses.models import Course
        course = Course.objects.get(id=course_id)
        
        enrollments = Enrollment.objects.filter(course=course, status='enrolled')
        summaries = []
        
        for enrollment in enrollments:
            summary, created = AttendanceSummary.objects.get_or_create(enrollment=enrollment)
            summaries.append(AttendanceSummarySerializer(summary).data)
        
        return Response({
            'course': course.code,
            'course_name': course.name,
            'attendance_summaries': summaries
        })
        
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
