from django.contrib import admin
from .models import TimeSlot, Schedule, Timetable, ClassConflict

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'is_active']
    list_filter = ['day', 'is_active']
    ordering = ['day', 'start_time']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'time_slot', 'room', 'semester', 'academic_year', 'instructor', 'is_active']
    list_filter = ['semester', 'academic_year', 'is_active', 'time_slot__day']
    search_fields = ['course__code', 'course__name', 'room', 'instructor__username']
    ordering = ['academic_year', 'semester', 'time_slot']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['user', 'semester', 'academic_year', 'generated_at']
    list_filter = ['semester', 'academic_year']
    search_fields = ['user__username']
    ordering = ['-academic_year', '-semester']

@admin.register(ClassConflict)
class ClassConflictAdmin(admin.ModelAdmin):
    list_display = ['schedule1', 'schedule2', 'conflict_type', 'resolved', 'detected_at']
    list_filter = ['conflict_type', 'resolved', 'detected_at']
    ordering = ['-detected_at']
