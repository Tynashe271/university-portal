from rest_framework import serializers
from .models import AdminPermission, SystemLog
from students.models import User

class AdminPermissionSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.username', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = AdminPermission
        fields = ['id', 'admin', 'admin_name', 'permission', 'granted_at', 'granted_by', 'granted_by_name']
        read_only_fields = ['id', 'granted_at']

class SystemLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SystemLog
        fields = ['id', 'action', 'user', 'username', 'model_name', 'object_id', 
                  'description', 'ip_address', 'timestamp']
        read_only_fields = ['id', 'timestamp']