from django.contrib import admin
from .models import Announcement, AnnouncementRead

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'priority', 'target_audience', 'published', 'publish_date', 'is_active']
    list_filter = ['priority', 'target_audience', 'published', 'publish_date']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-publish_date']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['announcement__title', 'user__username']
    ordering = ['-read_at']
