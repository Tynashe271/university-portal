from django.contrib import admin
from .models import Club, ClubMembership, ClubEvent, Achievement

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'coach', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ['club', 'student', 'role', 'status']
    list_filter = ['role', 'status']
    search_fields = ['student__username', 'club__name']

@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ['club', 'title', 'event_type', 'event_date', 'result']
    list_filter = ['event_type', 'result']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'student', 'level', 'date_achieved']
    list_filter = ['level']
