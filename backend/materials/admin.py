from django.contrib import admin
from .models import CourseMaterial, MaterialFolder

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'uploaded_by', 'upload_date', 'is_public', 'download_count']
    list_filter = ['material_type', 'is_public', 'upload_date']
    search_fields = ['title', 'description', 'course__code']
    ordering = ['-upload_date']

@admin.register(MaterialFolder)
class MaterialFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'parent_folder', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'course__code']
    ordering = ['order', 'name']
