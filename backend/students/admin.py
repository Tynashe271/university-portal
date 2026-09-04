from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'student_id', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'enrollment_date']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id']
    ordering = ['username']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'student_id', 'phone', 'date_of_birth', 'address', 'profile_picture')}),
    )
