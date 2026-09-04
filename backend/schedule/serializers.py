from rest_framework import serializers
from .models import TimeSlot, Schedule, Timetable, ClassConflict

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'day', 'start_time', 'end_time', 'is_active']
        read_only_fields = ['id']

class ScheduleSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'course', 'course_code', 'course_name', 'time_slot', 'time_slot_details', 
                  'room', 'semester', 'academic_year', 'instructor', 'instructor_name', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TimetableSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = ['id', 'user', 'user_name', 'semester', 'academic_year', 'generated_at', 'schedules']
        read_only_fields = ['id', 'generated_at', 'schedules']
    
    def get_schedules(self, obj):
        user = obj.user
        schedules = Schedule.objects.filter(
            semester=obj.semester,
            academic_year=obj.academic_year,
            is_active=True
        )
        
        if user.is_student():
            # Get schedules for courses the student is enrolled in
            from courses.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                student=user,
                status='enrolled',
                semester=obj.semester,
                academic_year=obj.academic_year
            ).values_list('course_id', flat=True)
            schedules = schedules.filter(course_id__in=enrolled_courses)
        elif user.is_admin_user():
            # Get schedules for courses the instructor teaches
            schedules = schedules.filter(instructor=user)
        
        return ScheduleSerializer(schedules, many=True).data

class ClassConflictSerializer(serializers.ModelSerializer):
    schedule1_details = ScheduleSerializer(source='schedule1', read_only=True)
    schedule2_details = ScheduleSerializer(source='schedule2', read_only=True)
    
    class Meta:
        model = ClassConflict
        fields = ['id', 'schedule1', 'schedule1_details', 'schedule2', 'schedule2_details', 
                  'conflict_type', 'detected_at', 'resolved']
        read_only_fields = ['id', 'detected_at']