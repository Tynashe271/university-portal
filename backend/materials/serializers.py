from rest_framework import serializers
from .models import CourseMaterial, MaterialFolder

class CourseMaterialSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    
    class Meta:
        model = CourseMaterial
        fields = ['id', 'course', 'course_code', 'course_name', 'folder', 'folder_name', 'title', 'description', 
                  'material_type', 'file', 'url', 'uploaded_by', 'uploaded_by_name', 
                  'upload_date', 'updated_date', 'is_public', 'download_count', 'order']
        read_only_fields = ['id', 'upload_date', 'updated_date', 'download_count']

class MaterialFolderSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialFolder
        fields = ['id', 'course', 'course_code', 'name', 'description', 'parent_folder', 
                  'created_by', 'created_by_name', 'created_at', 'order', 'materials_count']
        read_only_fields = ['id', 'created_at', 'materials_count']
    
    def get_materials_count(self, obj):
        return obj.materials.count()