from django.contrib import admin
from .models import Classroom, Department, Subject, Term

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'compulsory']
    list_filter = ['department', 'compulsory']

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'term', 'start_date', 'end_date', 'is_current']
    list_filter = ['academic_year', 'is_current']

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'stream', 'academic_year', 'capacity', 'class_teacher']
    list_filter = ['grade', 'academic_year']
