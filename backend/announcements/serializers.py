from rest_framework import serializers
from .models import Announcement, AnnouncementRead

class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    course_code = serializers.CharField(source='target_course.code', read_only=True)
    course_name = serializers.CharField(source='target_course.name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    read_count = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'author', 'author_name', 'priority', 
                  'target_audience', 'target_course', 'course_code', 'course_name', 
                  'published', 'publish_date', 'expiry_date', 'created_at', 'updated_at', 
                  'is_active', 'read_count', 'is_read']
        read_only_fields = ['id', 'publish_date', 'created_at', 'updated_at', 'is_active', 'read_count', 'is_read']
    
    def get_read_count(self, obj):
        return obj.reads.count()
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AnnouncementRead.objects.filter(
                announcement=obj, 
                user=request.user
            ).exists()
        return False

class AnnouncementReadSerializer(serializers.ModelSerializer):
    announcement_title = serializers.CharField(source='announcement.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AnnouncementRead
        fields = ['id', 'announcement', 'announcement_title', 'user', 'user_name', 'read_at']
        read_only_fields = ['id', 'read_at']