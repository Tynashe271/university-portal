from django.contrib import admin
from .models import FeeStructure, FeeAccount, FeePayment, FeeDiscount, Scholarship, ScholarshipApplication, InstallmentPlan, Installment, LateFeeConfig

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'fee_type', 'grade_level', 'academic_year', 'amount', 'is_active']
    list_filter = ['fee_type', 'grade_level', 'academic_year', 'is_active']
    search_fields = ['name', 'grade_level']

@admin.register(FeeAccount)
class FeeAccountAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'total_fees', 'fees_paid', 'fees_due', 'is_active']
    list_filter = ['academic_year', 'is_active']
    search_fields = ['student__username']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'fee_account', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['receipt_number', 'fee_account__student__username']

@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'discount_percentage', 'is_active']
    list_filter = ['discount_type', 'is_active']

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['name', 'scholarship_type', 'scholarship_percentage', 'total_slots', 'is_active']
    list_filter = ['scholarship_type', 'is_active']

@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ['scholarship', 'student', 'status', 'application_date']
    list_filter = ['status', 'scholarship']

@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'total_amount', 'number_of_installments', 'is_active']
    list_filter = ['academic_year', 'is_active']

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ['installment_plan', 'installment_number', 'due_date', 'amount', 'is_paid']
    list_filter = ['is_paid']

@admin.register(LateFeeConfig)
class LateFeeConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'fee_structure', 'grace_period_days', 'penalty_percentage', 'is_active']
    list_filter = ['is_active']