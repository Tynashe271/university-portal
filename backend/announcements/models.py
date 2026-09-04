from django.db import models
from students.models import User
from courses.models import Course

class Announcement(models.Model):
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TARGET_AUDIENCE = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('admins', 'Admins Only'),
        ('course', 'Specific Course'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    target_audience = models.CharField(max_length=10, choices=TARGET_AUDIENCE, default='all')
    target_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-publish_date', '-priority']
        
    def __str__(self):
        return f"{self.title} ({self.priority})"
    
    def is_active(self):
        from django.utils import timezone
        if not self.published:
            return False
        if self.expiry_date and self.expiry_date < timezone.now():
            return False
        return True

class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_announcements')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'announcement_reads'
        unique_together = ['announcement', 'user']
        
    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"
