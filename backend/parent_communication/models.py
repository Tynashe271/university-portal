from django.db import models
from django.conf import settings
from django.utils import timezone

class ParentProfile(models.Model):
    """Parent profile linked to students"""
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    occupation = models.CharField(max_length=200, blank=True)
    work_phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    emergency_contact = models.BooleanField(default=False)
    receives_sms = models.BooleanField(default=True)
    receives_email = models.BooleanField(default=True)
    receives_push = models.BooleanField(default=True)
    receives_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parent_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.relationship}"

class StudentParentRelation(models.Model):
    """Link between students and parents"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_relations')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_relations')
    relationship = models.CharField(max_length=20, choices=[('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')])
    is_primary_contact = models.BooleanField(default=False)
    pickup_permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_parent_relations'
        unique_together = ['student', 'parent']
    
    def __str__(self):
        return f"{self.student.username} - {self.parent.username}"

class Message(models.Model):
    """Messages between teachers and parents"""
    MESSAGE_TYPE_CHOICES = [
        ('direct', 'Direct Message'),
        ('announcement', 'Announcement'),
        ('emergency', 'Emergency'),
        ('academic', 'Academic'),
        ('behavioral', 'Behavioral'),
        ('attendance', 'Attendance'),
        ('fee', 'Fee Related'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='direct')
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    attachment = models.FileField(upload_to='messages/', blank=True)
    priority = models.CharField(max_length=10, choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')], default='normal')
    
    class Meta:
        db_table = 'messages'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.subject}"

class ConferenceSchedule(models.Model):
    """Parent-teacher conference scheduling"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conferences')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_conferences')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_conferences')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conference_schedules'
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.teacher.username} - {self.scheduled_date}"

class ParentNotification(models.Model):
    """Notifications for parents"""
    NOTIFICATION_TYPE_CHOICES = [
        ('attendance', 'Attendance'),
        ('grade', 'Grade'),
        ('fee', 'Fee'),
        ('announcement', 'Announcement'),
        ('emergency', 'Emergency'),
        ('conference', 'Conference'),
        ('behavioral', 'Behavioral'),
        ('general', 'General'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    sent_via_sms = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)
    sent_via_whatsapp = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_notifications')
    
    class Meta:
        db_table = 'parent_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

class DailySummary(models.Model):
    """Daily summary for parents (Day-in-Review)"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    attendance_status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('half_day', 'Half Day')])
    meals_consumed = models.JSONField(default=dict)  # {"breakfast": true, "lunch": true}
    mood = models.CharField(max_length=20, choices=[('happy', 'Happy'), ('sad', 'Sad'), ('neutral', 'Neutral'), ('excited', 'Excited')], blank=True)
    activities = models.TextField(blank=True)
    grades_received = models.JSONField(default=list)  # List of grades if any
    teacher_notes = models.TextField(blank=True)
    behavioral_notes = models.TextField(blank=True)
    homework_completed = models.BooleanField(default=True)
    sent_to_parents = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_summaries'
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date}"

class FeedbackForm(models.Model):
    """Feedback forms for parents"""
    FEEDBACK_TYPE_CHOICES = [
        ('safety', 'Safety'),
        ('workload', 'Workload'),
        ('satisfaction', 'Satisfaction'),
        ('teaching', 'Teaching Quality'),
        ('facilities', 'Facilities'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    description = models.TextField()
    questions = models.JSONField(default=list)  # List of questions
    is_anonymous = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback_forms'
    
    def __str__(self):
        return f"{self.title} - {self.feedback_type}"

class FeedbackResponse(models.Model):
    """Feedback responses from parents"""
    feedback_form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE, related_name='responses')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_responses')
    responses = models.JSONField(default=dict)  # Question ID: Answer
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'feedback_responses'
        unique_together = ['feedback_form', 'parent']
    
    def __str__(self):
        return f"{self.parent.username} - {self.feedback_form.title}"

class AnnouncementReadReceipt(models.Model):
    """Track announcement read receipts"""
    announcement = models.ForeignKey('announcements.Announcement', on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcement_receipts')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'announcement_read_receipts'
        unique_together = ['announcement', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.announcement.title}"