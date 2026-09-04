from django.db import models
from students.models import User

class AdminPermission(models.Model):
    PERMISSION_CHOICES = [
        ('manage_users', 'Manage Users'),
        ('manage_courses', 'Manage Courses'),
        ('manage_enrollments', 'Manage Enrollments'),
        ('manage_grades', 'Manage Grades'),
        ('view_reports', 'View Reports'),
        ('system_settings', 'System Settings'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    
    class Meta:
        db_table = 'admin_permissions'
        unique_together = ['admin', 'permission']
        ordering = ['-granted_at']
        
    def __str__(self):
        return f"{self.admin.username} - {self.permission}"

class SystemLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs')
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.model_name}"


class SchoolSettings(models.Model):
    """Single-row school-wide configuration. Use SchoolSettings.load() to
    get the one instance, creating it with sensible defaults on first use,
    rather than instantiating the model directly."""
    school_name = models.CharField(max_length=200, default='Anyschool High School')
    motto = models.CharField(max_length=300, blank=True, default='Learning with purpose, character and ambition.')
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    current_academic_year = models.CharField(max_length=10, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'school_settings'

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce a single row
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.school_name
