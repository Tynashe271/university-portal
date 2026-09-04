from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import TimeSlot, Schedule, Timetable, ClassConflict
from .serializers import TimeSlotSerializer, ScheduleSerializer, TimetableSerializer, ClassConflictSerializer
from courses.models import Course, Enrollment
from students.models import User

class TimeSlotListCreateView(generics.ListCreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user():
            return TimeSlot.objects.all()
        return TimeSlot.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only admins can create time slots")

class TimeSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            serializer.save()
        else:
            raise PermissionError("Only admins can update time slots")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only admins can delete time slots")

class ScheduleListCreateView(generics.ListCreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        semester = self.request.query_params.get('semester', None)
        academic_year = self.request.query_params.get('academic_year', None)
        course_id = self.request.query_params.get('course', None)
        
        queryset = Schedule.objects.filter(is_active=True)
        
        if semester:
            queryset = queryset.filter(semester=semester)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if user.is_student():
            # Get schedules for courses the student is enrolled in
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled'
            ).values_list('course_id', flat=True)
            return queryset.filter(course_id__in=enrolled_courses)
        elif user.is_admin_user():
            # Get schedules for courses the instructor teaches
            return queryset.filter(instructor=user)
        return Schedule.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            schedule = serializer.save(instructor=user)
            # Check for conflicts
            self.check_for_conflicts(schedule)
        else:
            raise PermissionError("Only admins can create schedules")
    
    def check_for_conflicts(self, new_schedule):
        # Check for time conflicts
        time_conflicts = Schedule.objects.filter(
            time_slot=new_schedule.time_slot,
            semester=new_schedule.semester,
            academic_year=new_schedule.academic_year,
            is_active=True
        ).exclude(id=new_schedule.id)
        
        for conflict in time_conflicts:
            # Check room conflict
            if conflict.room == new_schedule.room and new_schedule.room:
                ClassConflict.objects.get_or_create(
                    schedule1=new_schedule,
                    schedule2=conflict,
                    conflict_type='room'
                )
            
            # Check instructor conflict
            if conflict.instructor == new_schedule.instructor and new_schedule.instructor:
                ClassConflict.objects.get_or_create(
                    schedule1=new_schedule,
                    schedule2=conflict,
                    conflict_type='instructor'
                )

class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled'
            ).values_list('course_id', flat=True)
            return Schedule.objects.filter(course_id__in=enrolled_courses, is_active=True)
        elif user.is_admin_user():
            return Schedule.objects.filter(instructor=user, is_active=True)
        return Schedule.objects.none()
    
    def perform_update(self, serializer):
        user = self.request.user
        if user.is_admin_user():
            schedule = serializer.save()
            self.check_for_conflicts(schedule)
        else:
            raise PermissionError("Only admins can update schedules")
    
    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_admin_user():
            instance.delete()
        else:
            raise PermissionError("Only admins can delete schedules")
    
    def check_for_conflicts(self, new_schedule):
        time_conflicts = Schedule.objects.filter(
            time_slot=new_schedule.time_slot,
            semester=new_schedule.semester,
            academic_year=new_schedule.academic_year,
            is_active=True
        ).exclude(id=new_schedule.id)
        
        for conflict in time_conflicts:
            if conflict.room == new_schedule.room and new_schedule.room:
                ClassConflict.objects.get_or_create(
                    schedule1=new_schedule,
                    schedule2=conflict,
                    conflict_type='room'
                )
            
            if conflict.instructor == new_schedule.instructor and new_schedule.instructor:
                ClassConflict.objects.get_or_create(
                    schedule1=new_schedule,
                    schedule2=conflict,
                    conflict_type='instructor'
                )

class TimetableListView(generics.ListAPIView):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        semester = self.request.query_params.get('semester', None)
        academic_year = self.request.query_params.get('academic_year', None)
        
        queryset = Timetable.objects.filter(user=user)
        
        if semester:
            queryset = queryset.filter(semester=semester)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        
        return queryset

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_timetable(request):
    user = request.user
    semester = request.data.get('semester')
    academic_year = request.data.get('academic_year')
    
    if not semester or not academic_year:
        return Response({'error': 'Semester and academic year are required'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    # Create or get timetable
    timetable, created = Timetable.objects.get_or_create(
        user=user,
        semester=semester,
        academic_year=academic_year
    )
    
    return Response(TimetableSerializer(timetable).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_schedule(request):
    user = request.user
    semester = request.query_params.get('semester', 'Fall')
    academic_year = request.query_params.get('academic_year', '2026-2027')
    
    schedules = Schedule.objects.filter(
        semester=semester,
        academic_year=academic_year,
        is_active=True
    )
    
    if user.is_student():
        enrolled_courses = Enrollment.objects.filter(
            student=user,
            status='enrolled',
            semester=semester,
            academic_year=academic_year
        ).values_list('course_id', flat=True)
        schedules = schedules.filter(course_id__in=enrolled_courses)
    elif user.is_admin_user():
        schedules = schedules.filter(instructor=user)
    
    return Response(ScheduleSerializer(schedules, many=True).data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def detect_conflicts(request):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    conflicts = ClassConflict.objects.filter(resolved=False)
    return Response(ClassConflictSerializer(conflicts, many=True).data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resolve_conflict(request, conflict_id):
    user = request.user
    
    if not user.is_admin_user():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        conflict = ClassConflict.objects.get(id=conflict_id)
        conflict.resolved = True
        conflict.save()
        return Response({'message': 'Conflict resolved'}, status=status.HTTP_200_OK)
    except ClassConflict.DoesNotExist:
        return Response({'error': 'Conflict not found'}, status=status.HTTP_404_NOT_FOUND)
