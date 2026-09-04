from django.contrib import admin
from .models import AdmissionApplication, AdmissionDocument, MeritList, Waitlist

@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'student_name', 'grade_applying_for', 'status', 'submitted_date']
    list_filter = ['status', 'grade_applying_for', 'academic_year']
    search_fields = ['application_number', 'student_name', 'parent_name']
    readonly_fields = ['application_number', 'created_at', 'updated_at']

@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['application__application_number', 'document_type']

@admin.register(MeritList)
class MeritListAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'grade_level', 'cutoff_score', 'total_seats', 'is_active']
    list_filter = ['academic_year', 'grade_level', 'is_active']

@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['application', 'position', 'status', 'estimated_admission_date']
    list_filter = ['status']
    search_fields = ['application__student_name']