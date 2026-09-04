from rest_framework import serializers
from .models import TimeSlot, Schedule, Timetable, ClassConflict, ClassPeriod

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

class ClassPeriodSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True, default=None)
    time_slot_details = TimeSlotSerializer(source='time_slot', read_only=True)
    room = serializers.SerializerMethodField()

    class Meta:
        model = ClassPeriod
        fields = ['id', 'classroom', 'classroom_name', 'subject', 'subject_name', 'teacher',
                  'teacher_name', 'time_slot', 'time_slot_details', 'room', 'academic_year']
        read_only_fields = ['id']

    def get_room(self, obj):
        return obj.effective_room()

    def validate(self, data):
        classroom = data.get('classroom', getattr(self.instance, 'classroom', None))
        teacher = data.get('teacher', getattr(self.instance, 'teacher', None))
        time_slot = data.get('time_slot', getattr(self.instance, 'time_slot', None))
        academic_year = data.get('academic_year', getattr(self.instance, 'academic_year', None))

        # A teacher can't be in two classrooms during the same time slot —
        # the DB's unique_together only stops a classroom double-booking
        # itself, not a shared teacher, so that's checked here instead.
        if teacher and time_slot and academic_year:
            clash = ClassPeriod.objects.filter(
                teacher=teacher, time_slot=time_slot, academic_year=academic_year
            )
            if self.instance:
                clash = clash.exclude(pk=self.instance.pk)
            if classroom:
                clash = clash.exclude(classroom=classroom)
            existing = clash.first()
            if existing:
                raise serializers.ValidationError(
                    f"{teacher.name()} is already teaching {existing.classroom.name} at this time."
                )
        return data


class ClassConflictSerializer(serializers.ModelSerializer):
    schedule1_details = ScheduleSerializer(source='schedule1', read_only=True)
    schedule2_details = ScheduleSerializer(source='schedule2', read_only=True)
    
    class Meta:
        model = ClassConflict
        fields = ['id', 'schedule1', 'schedule1_details', 'schedule2', 'schedule2_details', 
                  'conflict_type', 'detected_at', 'resolved']
        read_only_fields = ['id', 'detected_at']