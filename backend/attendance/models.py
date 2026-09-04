from django.db import models
from courses.models import Course, Enrollment
from students.models import User

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    VERIFICATION_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('biometric', 'Biometric'),
        ('fingerprint', 'Fingerprint'),
        ('facial_recognition', 'Facial Recognition'),
        ('rfid', 'RFID Card'),
        ('gps', 'GPS Geofencing'),
        ('offline', 'Offline Capture'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    verification_method = models.CharField(max_length=30, choices=VERIFICATION_METHOD_CHOICES, default='manual')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    biometric_data = models.CharField(max_length=500, blank=True)  # Encrypted biometric data
    offline_synced = models.BooleanField(default=False)
    offline_device_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_records'
        unique_together = ['enrollment', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.date} ({self.status})"

class AttendanceSession(models.Model):
    ATTENDANCE_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('biometric', 'Biometric'),
        ('fingerprint', 'Fingerprint'),
        ('facial_recognition', 'Facial Recognition'),
        ('rfid', 'RFID Card'),
        ('gps', 'GPS Geofencing'),
        ('offline', 'Offline Capture'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    attendance_method = models.CharField(max_length=30, choices=ATTENDANCE_METHOD_CHOICES, default='manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    location = models.CharField(max_length=200, blank=True, null=True)
    geofence_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geofence_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geofence_radius = models.IntegerField(default=100)  # meters
    topic = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_sessions'
        unique_together = ['course', 'date', 'start_time']
        ordering = ['-date', '-start_time']
        
    def __str__(self):
        return f"{self.course.code} - {self.date} {self.start_time}"

class AttendanceSummary(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='attendance_summary')
    total_classes = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    chronic_absent_alert = models.BooleanField(default=False)
    improvement_trend = models.CharField(max_length=20, choices=[('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining')], blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_summaries'
        
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.attendance_percentage}%"
    
    def calculate_percentage(self):
        if self.total_classes > 0:
            # Calculate attendance (present + late + excused) / total * 100
            effective_attendance = self.present_count + self.late_count + self.excused_count
            self.attendance_percentage = (effective_attendance / self.total_classes) * 100
        else:
            self.attendance_percentage = 0.00
        self.save()

class AttendanceNotification(models.Model):
    """Real-time absence notification to parents (Feature 20)"""
    NOTIFICATION_TYPE_CHOICES = [
        ('absence', 'Absence Alert'),
        ('late', 'Late Arrival'),
        ('leave', 'Leave Notification'),
        ('weekly_summary', 'Weekly Summary'),
        ('monthly_summary', 'Monthly Summary'),
    ]
    
    NOTIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=NOTIFICATION_STATUS_CHOICES, default='pending')
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_attendance_alerts')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.notification_type}"

class BiometricTemplate(models.Model):
    """Biometric templates for students and staff (Feature 17)"""
    BIOMETRIC_TYPE_CHOICES = [
        ('fingerprint', 'Fingerprint'),
        ('face', 'Face Recognition'),
        ('iris', 'Iris Scan'),
        ('voice', 'Voice Recognition'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biometric_templates')
    biometric_type = models.CharField(max_length=20, choices=BIOMETRIC_TYPE_CHOICES)
    template_data = models.TextField()  # Encrypted biometric template
    device_id = models.CharField(max_length=100)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'biometric_templates'
        unique_together = ['user', 'biometric_type', 'device_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.biometric_type}"

class AttendanceKiosk(models.Model):
    """Attendance kiosk information (Feature 17)"""
    KIOSK_TYPE_CHOICES = [
        ('main_gate', 'Main Gate'),
        ('classroom', 'Classroom'),
        ('bus_stop', 'Bus Stop'),
        ('cafeteria', 'Cafeteria'),
    ]
    
    kiosk_id = models.CharField(max_length=50, unique=True)
    kiosk_name = models.CharField(max_length=200)
    kiosk_type = models.CharField(max_length=20, choices=KIOSK_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=50, blank=True)
    device_id = models.CharField(max_length=100, unique=True)
    supports_biometric = models.BooleanField(default=False)
    supports_gps = models.BooleanField(default=False)
    supports_offline = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_kiosks'
        ordering = ['kiosk_name']
    
    def __str__(self):
        return f"{self.kiosk_name} - {self.kiosk_type}"
