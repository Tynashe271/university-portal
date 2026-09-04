from rest_framework import serializers
from .models import Forum, Thread, Reply, ForumLike, ForumSubscription

class ForumSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    thread_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Forum
        fields = ['id', 'course', 'course_code', 'course_name', 'name', 'description', 
                  'forum_type', 'created_by', 'created_by_name', 'created_at', 
                  'is_active', 'is_public', 'thread_count']
        read_only_fields = ['id', 'created_at', 'thread_count']

class ReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    child_replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Reply
        fields = ['id', 'thread', 'content', 'author', 'author_name', 'author_role', 
                  'parent_reply', 'child_replies', 'created_at', 'updated_at', 'is_edited']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_edited']
    
    def get_child_replies(self, obj):
        child_replies = obj.child_replies.all()
        return ReplySerializer(child_replies, many=True).data

class ThreadSerializer(serializers.ModelSerializer):
    forum_name = serializers.CharField(source='forum.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)
    reply_count = serializers.ReadOnlyField()
    last_reply = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Thread
        fields = ['id', 'forum', 'forum_name', 'title', 'content', 'author', 'author_name', 
                  'author_role', 'created_at', 'updated_at', 'is_pinned', 'is_locked', 
                  'is_announcement', 'views', 'reply_count', 'last_reply', 'likes_count', 'is_liked']
        read_only_fields = ['id', 'created_at', 'updated_at', 'views', 'reply_count', 'last_reply', 'likes_count', 'is_liked']
    
    def get_last_reply(self, obj):
        last_reply = obj.last_reply
        if last_reply:
            return {
                'author': last_reply.author.username if last_reply.author else 'Unknown',
                'created_at': last_reply.created_at
            }
        return None
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ForumLike.objects.filter(thread=obj, user=request.user).exists()
        return False

class ForumLikeSerializer(serializers.ModelSerializer):
    thread_title = serializers.CharField(source='thread.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ForumLike
        fields = ['id', 'thread', 'thread_title', 'user', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class ForumSubscriptionSerializer(serializers.ModelSerializer):
    forum_name = serializers.CharField(source='forum.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ForumSubscription
        fields = ['id', 'forum', 'forum_name', 'user', 'user_name', 'subscribed_at', 
                  'notify_on_new_thread', 'notify_on_reply']
        read_only_fields = ['id', 'subscribed_at']