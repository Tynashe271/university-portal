from django.contrib import admin
from .models import QuestionBank, ExamPaper, ExamQuestion, ExamSchedule, StudentExamResult, ReEvaluationRequest, OnlineExam, OnlineExamAttempt

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'subject', 'chapter', 'difficulty', 'marks']
    list_filter = ['question_type', 'subject', 'difficulty']
    search_fields = ['question_text', 'subject', 'chapter']

@admin.register(ExamPaper)
class ExamPaperAdmin(admin.ModelAdmin):
    list_display = ['exam_name', 'exam_type', 'subject', 'grade_level', 'total_marks', 'duration_minutes']
    list_filter = ['exam_type', 'subject', 'grade_level']
    search_fields = ['exam_name', 'subject']

@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ['exam_paper', 'question_number', 'question', 'marks']
    list_filter = ['exam_paper']

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam_paper', 'exam_date', 'venue', 'invigilator', 'grade_level']
    list_filter = ['exam_date', 'grade_level']
    search_fields = ['exam_paper__exam_name', 'venue']

@admin.register(StudentExamResult)
class StudentExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_schedule', 'marks_obtained', 'percentage', 'grade', 'rank']
    list_filter = ['exam_schedule']
    search_fields = ['student__username']

@admin.register(ReEvaluationRequest)
class ReEvaluationRequestAdmin(admin.ModelAdmin):
    list_display = ['exam_result', 'student', 'status', 'original_marks', 'revised_marks']
    list_filter = ['status']
    search_fields = ['student__username']

@admin.register(OnlineExam)
class OnlineExamAdmin(admin.ModelAdmin):
    list_display = ['exam_paper', 'start_time', 'end_time', 'status', 'proctoring_type']
    list_filter = ['status', 'proctoring_type']

@admin.register(OnlineExamAttempt)
class OnlineExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['online_exam', 'student', 'start_time', 'score', 'is_submitted']
    list_filter = ['is_submitted']
    search_fields = ['student__username']