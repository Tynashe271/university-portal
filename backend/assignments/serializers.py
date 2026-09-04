from rest_framework import serializers
from .models import Assignment, AssignmentSubmission, AssignmentAttachment

class AssignmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = ['id', 'course', 'course_code', 'course_name', 'title', 'description', 
                  'assignment_type', 'total_points', 'due_date', 'created_by', 'created_by_name', 
                  'created_at', 'updated_at', 'is_published', 'allow_late_submission', 
                  'late_penalty_percentage', 'instructions', 'is_overdue', 'submission_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue', 'submission_count']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    course_code = serializers.CharField(source='assignment.course.code', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.username', read_only=True)
    final_grade = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'assignment_title', 'course_code', 'enrollment', 
                  'student', 'student_name', 'content', 'file', 'submitted_at', 'updated_at', 
                  'status', 'grade', 'feedback', 'graded_by', 'graded_by_name', 'graded_at', 
                  'is_late', 'final_grade']
        read_only_fields = ['id', 'submitted_at', 'updated_at', 'graded_at', 'final_grade']
    
    def get_final_grade(self, obj):
        if obj.grade:
            return obj.calculate_late_penalty()
        return None

class AssignmentAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = AssignmentAttachment
        fields = ['id', 'assignment', 'file', 'filename', 'uploaded_at', 'uploaded_by_name']
        read_only_fields = ['id', 'uploaded_at']