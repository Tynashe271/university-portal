from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
        ('driver', 'Driver'),
        ('attendant', 'Attendant'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Extended student information (Features 5-10)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # Academic history
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    previous_grade = models.CharField(max_length=10, blank=True, null=True)
    previous_school_address = models.TextField(blank=True, null=True)
    transfer_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Extracurricular activities
    interests = models.JSONField(default=list)  # List of interests/hobbies
    extracurricular_activities = models.JSONField(default=list)  # List of activities
    achievements = models.JSONField(default=list)  # List of achievements
    
    # Family information
    siblings = models.JSONField(default=list)  # List of sibling information
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_student(self):
        return self.role == 'student'
    
    def is_admin_user(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_staff_user(self):
        return self.role == 'staff'
    
    def is_driver(self):
        return self.role == 'driver'
    
    def is_attendant(self):
        return self.role == 'attendant'
    
    def generate_verification_token(self):
        self.email_verification_token = uuid.uuid4()
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token

class BehavioralIncident(models.Model):
    """Behavioral incident log (Feature 8)"""
    INCIDENT_TYPE_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavioral_incidents')
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    incident_date = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_behavioral_incidents')
    location = models.CharField(max_length=200, blank=True)
    action_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    parent_notified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'behavioral_incidents'
        ordering = ['-incident_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.incident_type} - {self.incident_date}"