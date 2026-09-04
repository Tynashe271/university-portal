from rest_framework import serializers
from .models import Department, Course, Enrollment, Grade
import re

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        if not re.match(r'^[A-Z]{2,5}$', value):
            raise serializers.ValidationError("Department code must be 2-5 uppercase letters.")
        return value
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Department name must be at least 3 characters long.")
        return value

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    available_seats = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'credits', 'level', 'department', 
                  'department_name', 'instructor', 'instructor_name', 'capacity', 'status', 
                  'prerequisite', 'enrolled_count', 'available_seats', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        if not re.match(r'^[A-Z]{2,4}\d{3}$', value):
            raise serializers.ValidationError("Course code must be in format like 'CS101' (2-4 letters followed by 3 numbers).")
        return value
    
    def validate_credits(self, value):
        if value < 1 or value > 6:
            raise serializers.ValidationError("Credits must be between 1 and 6.")
        return value
    
    def validate_capacity(self, value):
        if value < 1 or value > 500:
            raise serializers.ValidationError("Capacity must be between 1 and 500.")
        return value
    
    def validate(self, attrs):
        # Check if prerequisite is not the same as the course
        if attrs.get('prerequisite') and attrs.get('code'):
            if attrs['prerequisite'].code == attrs['code']:
                raise serializers.ValidationError("A course cannot be its own prerequisite.")
        return attrs

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_name', 'course', 'course_code', 'course_name', 
                  'status', 'enrollment_date', 'completion_date', 'semester', 'academic_year']
        read_only_fields = ['id', 'enrollment_date']
    
    def validate_academic_year(self, value):
        if not re.match(r'^\d{4}-\d{4}$', value):
            raise serializers.ValidationError("Academic year must be in format 'YYYY-YYYY'.")
        return value
    
    def validate_semester(self, value):
        valid_semesters = ['Fall', 'Spring', 'Summer', 'Winter']
        if value not in valid_semesters:
            raise serializers.ValidationError(f"Semester must be one of: {', '.join(valid_semesters)}.")
        return value

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='enrollment.student.username', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.code', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.username', read_only=True)
    
    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'student_name', 'course_code', 'midterm_grade', 
                  'final_grade', 'assignment_grade', 'overall_grade', 'letter_grade', 
                  'comments', 'graded_by', 'graded_by_name', 'graded_date']
        read_only_fields = ['id', 'graded_date']
    
    def validate_midterm_grade(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Midterm grade must be between 0 and 100.")
        return value
    
    def validate_final_grade(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Final grade must be between 0 and 100.")
        return value
    
    def validate_assignment_grade(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Assignment grade must be between 0 and 100.")
        return value