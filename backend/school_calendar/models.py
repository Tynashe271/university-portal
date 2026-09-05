from django.db import models
from django.conf import settings


class CalendarEvent(models.Model):
    """One shared school calendar for terms, holidays, exams, meetings,
    sports days, deadlines and assemblies — 'event_type' is what
    distinguishes them, rather than a separate model per kind."""
    EVENT_TYPE_CHOICES = [
        ('term', 'Term'),
        ('holiday', 'Holiday'),
        ('exam', 'Examination'),
        ('meeting', 'Meeting'),
        ('sports_day', 'Sports day'),
        ('trip', 'Trip'),
        ('deadline', 'Deadline'),
        ('assembly', 'Assembly'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    academic_year = models.CharField(max_length=10, blank=True)
    term = models.ForeignKey('academics.Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='calendar_events')
    is_public = models.BooleanField(default=True, help_text="Shown on the public-facing site, not just the admin dashboard")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'calendar_events'
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.start_date}"
