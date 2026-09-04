from django.conf import settings
from django.db import models


class NewsEvent(models.Model):
    """A public news article or event shown on the school website.

    Both kinds share one model since they render the same way (a card
    with a title, summary and date) — `category` just decides whether
    `event_date`/`location` are shown.
    """
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('event', 'Event'),
    ]

    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='news')

    # Events only — when/where it happens. Left blank for plain news posts.
    event_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)

    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='news_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"
