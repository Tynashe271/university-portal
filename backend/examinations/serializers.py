from rest_framework import serializers
from .models import QuestionBank, Assessment, Mark

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    term_label = serializers.CharField(source='term.get_term_display', read_only=True, default=None)
    marked_count = serializers.SerializerMethodField()
    class_average = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['id', 'name', 'subject', 'subject_name', 'classroom', 'classroom_name', 'term', 'term_label',
                  'assessment_type', 'max_score', 'date', 'published', 'created_by', 'created_at',
                  'marked_count', 'class_average']
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_marked_count(self, obj):
        return obj.marks.count()

    def get_class_average(self, obj):
        marks = list(obj.marks.all())
        if not marks:
            return None
        return round(sum(float(m.score) for m in marks) / len(marks), 1)


class MarkSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    percentage = serializers.FloatField(read_only=True)
    letter_grade = serializers.CharField(read_only=True)

    class Meta:
        model = Mark
        fields = ['id', 'assessment', 'student', 'student_name', 'score', 'percentage',
                  'letter_grade', 'comments', 'graded_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'graded_by', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.username

    def validate_score(self, value):
        assessment = self.initial_data.get('assessment') or getattr(self.instance, 'assessment_id', None)
        if assessment:
            from .models import Assessment
            try:
                max_score = Assessment.objects.get(pk=assessment).max_score
            except Assessment.DoesNotExist:
                return value
            if value > max_score:
                raise serializers.ValidationError(f"Score can't exceed the assessment's max score ({max_score}).")
        return value