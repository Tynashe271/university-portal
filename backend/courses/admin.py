from django.contrib import admin
from .models import Department, Course, Enrollment, Grade

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'level', 'credits', 'capacity', 'status']
    list_filter = ['level', 'status', 'department']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'semester', 'academic_year', 'enrollment_date']
    list_filter = ['status', 'semester', 'academic_year']
    search_fields = ['student__username', 'course__code']
    ordering = ['-enrollment_date']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'overall_grade', 'letter_grade', 'graded_by', 'graded_date']
    list_filter = ['letter_grade']
    search_fields = ['enrollment__student__username', 'enrollment__course__code']
    ordering = ['-graded_date']
