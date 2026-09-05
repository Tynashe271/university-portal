from django.contrib import admin
from .models import CalendarEvent

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'is_public']
    list_filter = ['event_type', 'is_public']
    search_fields = ['title']
