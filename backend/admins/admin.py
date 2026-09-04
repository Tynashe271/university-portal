from django.contrib import admin
from .models import AdminPermission, SystemLog

@admin.register(AdminPermission)
class AdminPermissionAdmin(admin.ModelAdmin):
    list_display = ['admin', 'permission', 'granted_at', 'granted_by']
    list_filter = ['permission', 'granted_at']
    search_fields = ['admin__username', 'permission']
    ordering = ['-granted_at']

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'model_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'description', 'model_name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
