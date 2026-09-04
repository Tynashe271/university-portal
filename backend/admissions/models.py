from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
import os

def upload_to(instance, filename):
    return os.path.join('admissions', str(instance.application_number), filename)

class AdmissionApplication(models.Model):
    """Admission application with document upload"""
    APPLICATION_STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('admitted', 'Admitted'),
        ('enrolled', 'Enrolled'),
    ]
    
    ACADEMIC_YEAR_CHOICES = [
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
    ]

    GRADE_LEVEL_CHOICES = [
        ('form1', 'Form 1'),
        ('form2', 'Form 2'),
        ('form3', 'Form 3'),
        ('form4', 'Form 4'),
        ('lower6', 'Lower 6'),
        ('upper6', 'Upper 6'),
    ]
    
    application_number = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    grade_applying_for = models.CharField(max_length=10, choices=GRADE_LEVEL_CHOICES)
    academic_year = models.CharField(max_length=10, choices=ACADEMIC_YEAR_CHOICES)
    
    # Parent Information
    parent_name = models.CharField(max_length=200)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20)
    parent_address = models.TextField()
    
    # Previous School Information
    previous_school = models.CharField(max_length=200, blank=True)
    previous_grade = models.CharField(max_length=10, blank=True)
    transfer_certificate = models.FileField(
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True
    )

    # Free-text extras collected on the public application form that don't
    # have a dedicated column (nationality, boarding preference, special
    # needs, relationship to guardian, payment reference, etc.)
    additional_notes = models.TextField(blank=True)

    # Portal password the applicant sets on the application form, issued
    # alongside the application_number so they can sign back in to check
    # their status. Stored hashed (see AdmissionApplicationSerializer),
    # never returned by the API.
    portal_password = models.CharField(max_length=128, blank=True)
    
    # Application Status
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='draft')
    submitted_date = models.DateTimeField(null=True, blank=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    
    # Admission Details
    merit_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    admission_letter = models.FileField(upload_to=upload_to, blank=True)
    fee_quotation = models.FileField(upload_to=upload_to, blank=True)

    # Points-based class placement (Form 1 only — see admissions/classing.py).
    # `points` is entered by admissions staff when they accept the
    # application; `assigned_class` is what the system placed them into
    # (e.g. "1-2"), left blank for applications with no points scheme.
    points = models.PositiveIntegerField(null=True, blank=True)
    assigned_class = models.CharField(max_length=10, blank=True)
    
    # Additional Documents
    birth_certificate = models.FileField(upload_to=upload_to, blank=True)
    photo = models.ImageField(upload_to=upload_to, blank=True)
    aadhar_card = models.FileField(upload_to=upload_to, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admission_applications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application_number} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            from django.utils import timezone
            year = timezone.now().year
            count = AdmissionApplication.objects.filter(created_at__year=year).count() + 1
            self.application_number = f"APP{year}{count:04d}"
        super().save(*args, **kwargs)

class AdmissionDocument(models.Model):
    """Additional documents for admission"""
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100)
    document_file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admission_documents'
    
    def __str__(self):
        return f"{self.application.application_number} - {self.document_type}"

class MeritList(models.Model):
    """Merit list for admissions"""
    academic_year = models.CharField(max_length=10)
    grade_level = models.CharField(max_length=10)
    cutoff_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_seats = models.IntegerField()
    published_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'merit_lists'
        unique_together = ['academic_year', 'grade_level']
    
    def __str__(self):
        return f"{self.grade_level} - {self.academic_year}"

class Waitlist(models.Model):
    """Waitlist management"""
    application = models.OneToOneField(AdmissionApplication, on_delete=models.CASCADE)
    position = models.IntegerField()
    estimated_admission_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('promoted', 'Promoted'), ('expired', 'Expired')], default='active')
    
    class Meta:
        db_table = 'waitlists'
        ordering = ['position']
    
    def __str__(self):
        return f"{self.application.student_name} - Position {self.position}"