from django.contrib import admin
from .models import Assignment, AssignmentSubmission, AssignmentAttachment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'assignment_type', 'due_date', 'total_points', 'is_published', 'created_by']
    list_filter = ['assignment_type', 'is_published', 'due_date', 'course']
    search_fields = ['title', 'description', 'course__code']
    ordering = ['-due_date']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'submitted_at', 'grade', 'is_late']
    list_filter = ['status', 'is_late', 'submitted_at']
    search_fields = ['assignment__title', 'student__username']
    ordering = ['-submitted_at']
    readonly_fields = ['submitted_at', 'updated_at', 'graded_at']

@admin.register(AssignmentAttachment)
class AssignmentAttachmentAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'filename', 'uploaded_at', 'uploaded_by']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'assignment__title']
    ordering = ['-uploaded_at']
