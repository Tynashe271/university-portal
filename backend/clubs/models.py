from django.db import models
from django.conf import settings


class Club(models.Model):
    """A club, society, or sports team — 'category' distinguishes a sports
    team from an academic/cultural society without needing separate models."""
    CATEGORY_CHOICES = [
        ('sport', 'Sport'),
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('community', 'Community service'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    coach = models.ForeignKey(
        'staff.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='clubs_coached'
    )
    meeting_day = models.CharField(max_length=20, blank=True, help_text="e.g. Wednesday")
    meeting_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clubs'
        ordering = ['name']

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('vice_captain', 'Vice-captain'),
        ('captain', 'Captain'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'club_memberships'
        unique_together = ['club', 'student']
        ordering = ['-joined_date']

    def __str__(self):
        return f"{self.student.username} - {self.club.name}"


class ClubEvent(models.Model):
    """A fixture, competition, or general meeting/event for a club."""
    EVENT_TYPE_CHOICES = [
        ('fixture', 'Fixture/Match'),
        ('competition', 'Competition'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('draw', 'Draw'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    opponent = models.CharField(max_length=200, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    event_date = models.DateTimeField()
    our_score = models.IntegerField(null=True, blank=True)
    opponent_score = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'club_events'
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.club.name} - {self.title}"


class Achievement(models.Model):
    """A recognition earned by a club or an individual student — e.g.
    'Runners-up, District Athletics 2026' or 'Best Debater, Inter-school'."""
    LEVEL_CHOICES = [
        ('school', 'School'),
        ('district', 'District'),
        ('provincial', 'Provincial'),
        ('national', 'National'),
        ('international', 'International'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True, related_name='achievements')
    # related_name is 'club_achievements', not 'achievements' — User already
    # has its own unrelated 'achievements' JSONField, and reusing the name
    # would silently overwrite that field's descriptor.
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='club_achievements'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='school')
    date_achieved = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'club_achievements'
        ordering = ['-date_achieved']

    def __str__(self):
        return self.title
