from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

class StaffProfile(models.Model):
    """Staff profiles with qualifications and experience"""
    EMPLOYEE_TYPE_CHOICES = [
        ('permanent_teacher', 'Permanent Teacher'),
        ('student_teacher', 'Student Teacher'),
        ('staff', 'Staff'),
        ('sdc_member', 'SDC Member'),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ]

    # A quick admin add doesn't require a login account — `user` links one
    # up later if the person needs portal access, `full_name`/`email` cover
    # a record added with nothing but a name and a category.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE_CHOICES)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    designation = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField(default=timezone.localdate)
    qualification = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    previous_experience = models.TextField(blank=True)
    certifications = models.JSONField(default=list)  # List of certifications
    skills = models.JSONField(default=list)  # List of skills
    subjects = models.JSONField(default=list)  # For teaching staff
    classes_assigned = models.JSONField(default=list)  # List of class assignments
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def name(self):
        if self.full_name:
            return self.full_name
        if self.user:
            return self.user.get_full_name() or self.user.username
        return 'Unnamed'

    def save(self, *args, **kwargs):
        if not self.employee_id:
            year = timezone.now().year
            count = StaffProfile.objects.filter(created_at__year=year).count() + 1
            self.employee_id = f"STF{year}{count:04d}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'staff_profiles'

    def __str__(self):
        return f"{self.name()} - {self.get_employee_type_display()}"

class LeaveManagement(models.Model):
    """Staff leave management"""
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('earned', 'Earned Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('emergency', 'Emergency Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leave_management'
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.staff.username} - {self.leave_type}"

class LeaveBalance(models.Model):
    """Leave balance for each staff member"""
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.CharField(max_length=20, choices=[('sick', 'Sick Leave'), ('casual', 'Casual Leave'), ('earned', 'Earned Leave')])
    total_allocated = models.IntegerField(default=0)
    used = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    academic_year = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'leave_balances'
        unique_together = ['staff', 'leave_type', 'academic_year']
    
    def __str__(self):
        return f"{self.staff.username} - {self.leave_type}: {self.remaining}"

class Payroll(models.Model):
    """Staff payroll management"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payroll')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    payment_month = models.CharField(max_length=20)  # e.g., "January 2024"
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=[('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('cheque', 'Cheque')])
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payroll'
        unique_together = ['staff', 'payment_month']
        ordering = ['-payment_month']
    
    def __str__(self):
        return f"{self.staff.username} - {self.payment_month}"

class PerformanceAppraisal(models.Model):
    """Staff performance appraisal"""
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appraisals')
    appraisal_period = models.CharField(max_length=20)  # e.g., "Q1 2024"
    teaching_quality = models.IntegerField(choices=RATING_CHOICES)
    student_engagement = models.IntegerField(choices=RATING_CHOICES)
    punctuality = models.IntegerField(choices=RATING_CHOICES)
    teamwork = models.IntegerField(choices=RATING_CHOICES)
    innovation = models.IntegerField(choices=RATING_CHOICES)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    appraiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='conducted_appraisals')
    appraisal_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_appraisals'
        unique_together = ['staff', 'appraisal_period']
        ordering = ['-appraisal_date']
    
    def __str__(self):
        return f"{self.staff.username} - {self.appraisal_period}"

class ProfessionalDevelopment(models.Model):
    """Professional development and training history"""
    TRAINING_TYPE_CHOICES = [
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('certification', 'Certification'),
        ('online_course', 'Online Course'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professional_development')
    training_name = models.CharField(max_length=300)
    training_type = models.CharField(max_length=20, choices=TRAINING_TYPE_CHOICES)
    institution = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    certificate_obtained = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='staff/certificates/', blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'professional_development'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.staff.username} - {self.training_name}"

class DocumentExpiryAlert(models.Model):
    """Document expiry alerts for staff"""
    DOCUMENT_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('work_permit', 'Work Permit'),
        ('police_clearance', 'Police Clearance'),
        ('medical_clearance', 'Medical Clearance'),
        ('teaching_license', 'Teaching License'),
        ('other', 'Other'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_alerts')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=200)
    expiry_date = models.DateField()
    alert_days_before = models.IntegerField(default=30)
    alert_sent = models.BooleanField(default=False)
    document_file = models.FileField(upload_to='staff/documents/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_expiry_alerts'
        ordering = ['expiry_date']
    
    def __str__(self):
        return f"{self.staff.username} - {self.document_name}"