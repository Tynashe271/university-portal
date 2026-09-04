from django.contrib import admin
from .models import NewsEvent

@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'event_date', 'published', 'created_by', 'created_at']
    list_filter = ['category', 'published']
    search_fields = ['title', 'summary', 'body']
    ordering = ['-created_at']
