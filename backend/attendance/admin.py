from django.contrib import admin
from .models import AttendanceRecord, AttendanceSession, AttendanceSummary

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'status', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['enrollment__student__username', 'enrollment__course__code']
    ordering = ['-date']

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'date', 'start_time', 'end_time', 'topic', 'created_by']
    list_filter = ['date', 'course']
    search_fields = ['course__code', 'topic']
    ordering = ['-date', '-start_time']

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'total_classes', 'present_count', 'absent_count', 'attendance_percentage']
    list_filter = ['attendance_percentage']
    search_fields = ['enrollment__student__username', 'enrollment__course__code']
    ordering = ['attendance_percentage']
