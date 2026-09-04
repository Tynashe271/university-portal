from django.contrib import admin
from .models import StaffProfile, LeaveManagement, LeaveBalance, Payroll, PerformanceAppraisal, ProfessionalDevelopment, DocumentExpiryAlert

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'employee_type', 'designation', 'department', 'employment_status']
    list_filter = ['employee_type', 'employment_status', 'department']
    search_fields = ['user__username', 'full_name', 'employee_id', 'designation']

@admin.register(LeaveManagement)
class LeaveManagementAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'total_days', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['staff__username']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'total_allocated', 'used', 'remaining', 'academic_year']
    list_filter = ['leave_type', 'academic_year']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['staff', 'payment_month', 'basic_salary', 'net_salary', 'payment_status']
    list_filter = ['payment_status', 'payment_month']
    search_fields = ['staff__username']

@admin.register(PerformanceAppraisal)
class PerformanceAppraisalAdmin(admin.ModelAdmin):
    list_display = ['staff', 'appraisal_period', 'overall_rating', 'appraisal_date']
    list_filter = ['appraisal_period']
    search_fields = ['staff__username']

@admin.register(ProfessionalDevelopment)
class ProfessionalDevelopmentAdmin(admin.ModelAdmin):
    list_display = ['staff', 'training_name', 'training_type', 'start_date', 'end_date']
    list_filter = ['training_type']
    search_fields = ['staff__username', 'training_name']

@admin.register(DocumentExpiryAlert)
class DocumentExpiryAlertAdmin(admin.ModelAdmin):
    list_display = ['staff', 'document_type', 'document_name', 'expiry_date', 'alert_sent']
    list_filter = ['document_type', 'alert_sent']
    search_fields = ['staff__username', 'document_name']