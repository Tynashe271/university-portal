from django.db import models
from django.conf import settings

class DailySELCheckIn(models.Model):
    """Daily Social-Emotional Learning emoji check-in"""
    EMOJI_CHOICES = [
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('excited', '🤩 Excited'),
        ('tired', '😴 Tired'),
        ('worried', '😟 Worried'),
        ('angry', '😠 Angry'),
        ('calm', '😌 Calm'),
        ('frustrated', '😤 Frustrated'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sel_checkins')
    date = models.DateField()
    mood = models.CharField(max_length=20, choices=EMOJI_CHOICES)
    sleep_quality = models.CharField(max_length=20, choices=[('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], blank=True)
    energy_level = models.CharField(max_length=20, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], blank=True)
    social_interaction = models.CharField(max_length=20, choices=[('great', 'Great'), ('good', 'Good'), ('okay', 'Okay'), ('difficult', 'Difficult')], blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_sel_checkins'
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.mood}"

class CounselingSession(models.Model):
    """Counseling session scheduling and confidential case notes"""
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('family', 'Family'),
        ('crisis', 'Crisis Intervention'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counseling_sessions')
    counselor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='conducted_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=45)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    session_notes = models.TextField(blank=True)
    is_confidential = models.BooleanField(default=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'counseling_sessions'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.scheduled_date}"

class IncidentReport(models.Model):
    """Peer bullying/incident anonymous reporting system"""
    INCIDENT_TYPE_CHOICES = [
        ('bullying', 'Bullying'),
        ('harassment', 'Harassment'),
        ('theft', 'Theft'),
        ('vandalism', 'Vandalism'),
        ('physical', 'Physical Altercation'),
        ('verbal', 'Verbal Abuse'),
        ('cyberbullying', 'Cyberbullying'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reported_wellbeing_incidents')
    is_anonymous = models.BooleanField(default=False)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPE_CHOICES)
    incident_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    involved_students = models.JSONField(default=list)  # List of student IDs if known
    witnesses = models.JSONField(default=list)  # List of witness names
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    severity = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    reported_date = models.DateTimeField(auto_now_add=True)
    investigated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='investigated_incidents')
    resolution_notes = models.TextField(blank=True)
    actions_taken = models.TextField(blank=True)
    
    class Meta:
        db_table = 'incident_reports'
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.incident_type} - {self.incident_date}"

class WellnessTrend(models.Model):
    """Wellness trend analytics - flagging distress patterns"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wellness_trends')
    analysis_period = models.CharField(max_length=20)  # e.g., "January 2024"
    mood_average = models.CharField(max_length=20, blank=True)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    academic_performance = models.CharField(max_length=20, choices=[('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining')], blank=True)
    social_engagement = models.CharField(max_length=20, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], blank=True)
    behavioral_incidents = models.IntegerField(default=0)
    counseling_sessions_count = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='low')
    risk_factors = models.JSONField(default=list)  # List of identified risk factors
    recommendations = models.TextField(blank=True)
    flagged_for_review = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_wellness_trends')
    review_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wellness_trends'
        unique_together = ['student', 'analysis_period']
        ordering = ['-analysis_period']
    
    def __str__(self):
        return f"{self.student.username} - {self.analysis_period} - {self.risk_level}"

class BehavioralReward(models.Model):
    """Behavioral reward system - positive behavior points & recognition"""
    REWARD_TYPE_CHOICES = [
        ('points', 'Points'),
        ('badge', 'Badge'),
        ('certificate', 'Certificate'),
        ('privilege', 'Privilege'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behavioral_rewards')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    points = models.IntegerField(default=0)
    badge_name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[('academic', 'Academic'), ('behavioral', 'Behavioral'), ('social', 'Social'), ('leadership', 'Leadership'), ('other', 'Other')])
    awarded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='awarded_rewards')
    awarded_date = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'behavioral_rewards'
        ordering = ['-awarded_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.reward_type} - {self.points}"

class PositiveBehaviorLog(models.Model):
    """Positive behavior logging"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='positive_behaviors')
    behavior = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[('helping', 'Helping Others'), ('leadership', 'Leadership'), ('academic', 'Academic Excellence'), ('kindness', 'Kindness'), ('integrity', 'Integrity'), ('other', 'Other')])
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reported_positive_behaviors')
    date = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'positive_behavior_logs'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.behavior}"