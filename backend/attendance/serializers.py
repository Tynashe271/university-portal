from rest_framework import serializers
from .models import AttendanceRecord, AttendanceSession, AttendanceSummary, DailyAttendance


class DailyAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    classroom_name = serializers.CharField(source='student.classroom.name', read_only=True, default=None)
    marked_by_name = serializers.CharField(source='marked_by.username', read_only=True, default=None)

    class Meta:
        model = DailyAttendance
        fields = ['id', 'student', 'student_name', 'student_id', 'classroom_name',
                  'date', 'status', 'reason', 'marked_by', 'marked_by_name', 'created_at']
        read_only_fields = ['id', 'marked_by', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='enrollment.student.username', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.code', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.username', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'enrollment', 'student_name', 'course_code', 'course_name', 
                  'date', 'status', 'notes', 'marked_by', 'marked_by_name', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AttendanceSessionSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSession
        fields = ['id', 'course', 'course_code', 'course_name', 'date', 'start_time', 
                  'end_time', 'topic', 'notes', 'created_by', 'created_by_name', 
                  'created_at', 'student_count']
        read_only_fields = ['id', 'created_at', 'student_count']
    
    def get_student_count(self, obj):
        return obj.course.enrollments.filter(status='enrolled').count()

class AttendanceSummarySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='enrollment.student.username', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.code', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    
    class Meta:
        model = AttendanceSummary
        fields = ['id', 'enrollment', 'student_name', 'course_code', 'course_name', 
                  'total_classes', 'present_count', 'absent_count', 'late_count', 
                  'excused_count', 'attendance_percentage', 'last_updated']
        read_only_fields = ['id', 'last_updated']