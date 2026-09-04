from rest_framework import serializers
from .models import Classroom, Department, Subject, Term


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    term_label = serializers.CharField(source='get_term_display', read_only=True)

    class Meta:
        model = Term
        fields = '__all__'


class ClassroomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    grade_label = serializers.CharField(source='get_grade_display', read_only=True)
    class_teacher_name = serializers.CharField(source='class_teacher.name', read_only=True, default=None)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = '__all__'

    def get_student_count(self, obj):
        from students.models import User
        return User.objects.filter(classroom=obj).count()
