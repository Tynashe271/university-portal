from django.contrib import admin
from .models import Forum, Thread, Reply, ForumLike, ForumSubscription

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum_type', 'course', 'is_active', 'is_public', 'created_by', 'created_at']
    list_filter = ['forum_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'course__code']
    ordering = ['name']

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'author', 'is_pinned', 'is_locked', 'is_announcement', 'views', 'created_at']
    list_filter = ['is_pinned', 'is_locked', 'is_announcement', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created_at']

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'parent_reply', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']

@admin.register(ForumLike)
class ForumLikeAdmin(admin.ModelAdmin):
    list_display = ['thread', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['thread__title', 'user__username']
    ordering = ['-created_at']

@admin.register(ForumSubscription)
class ForumSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['forum', 'user', 'notify_on_new_thread', 'notify_on_reply', 'subscribed_at']
    list_filter = ['notify_on_new_thread', 'notify_on_reply', 'subscribed_at']
    search_fields = ['forum__name', 'user__username']
    ordering = ['-subscribed_at']
