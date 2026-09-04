from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

class FeeStructure(models.Model):
    """Dynamic fee structure"""
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('transportation', 'Transportation Fee'),
        ('meals', 'Meals/Cafeteria Fee'),
        ('lab', 'Laboratory Fee'),
        ('library', 'Library Fee'),
        ('sports', 'Sports Fee'),
        ('extracurricular', 'Extracurricular Fee'),
        ('technology', 'Technology Fee'),
        ('admission', 'Admission Fee'),
        ('annual', 'Annual Fee'),
        ('other', 'Other'),
    ]
    
    # Matches admissions.AdmissionApplication.GRADE_LEVEL_CHOICES — this
    # school runs Form 1-6, not a Grade 1-12/Kindergarten system.
    GRADE_LEVEL_CHOICES = [
        ('form1', 'Form 1'),
        ('form2', 'Form 2'),
        ('form3', 'Form 3'),
        ('form4', 'Form 4'),
        ('lower6', 'Lower 6'),
        ('upper6', 'Upper 6'),
    ]

    ACADEMIC_YEAR_CHOICES = [
        ('2024-2025', '2024-2025'),
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
        ('2027-2028', '2027-2028'),
    ]
    
    name = models.CharField(max_length=200)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    grade_level = models.CharField(max_length=10, choices=GRADE_LEVEL_CHOICES)
    academic_year = models.CharField(max_length=10, choices=ACADEMIC_YEAR_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_structures'
        unique_together = ['fee_type', 'grade_level', 'academic_year']
    
    def __str__(self):
        return f"{self.name} - {self.grade_level} ({self.academic_year})"

class FeeAccount(models.Model):
    """Student fee account"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fee_accounts')
    academic_year = models.CharField(max_length=10)
    total_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fees_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fees_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_accounts'
        unique_together = ['student', 'academic_year']
    
    def __str__(self):
        return f"{self.student.username} - {self.academic_year}"
    
    def calculate_due(self):
        return self.total_fees - self.fees_paid - self.discount_amount - self.scholarship_amount + self.late_fee_penalty

class FeePayment(models.Model):
    """Fee payment records"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
        ('online', 'Online Payment Gateway'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    fee_account = models.ForeignKey(FeeAccount, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_generated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_payments')
    
    class Meta:
        db_table = 'fee_payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number or not self.transaction_id:
            from django.utils import timezone
            import uuid
            year = timezone.now().year
            count = FeePayment.objects.filter(payment_date__year=year).count() + 1
            if not self.receipt_number:
                self.receipt_number = f"RCP{year}{count:06d}"
            if not self.transaction_id:
                self.transaction_id = f"TXN{year}{count:06d}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class FeeDiscount(models.Model):
    """Discount structures"""
    DISCOUNT_TYPE_CHOICES = [
        ('sibling', 'Sibling Discount'),
        ('merit', 'Merit-based Discount'),
        ('early_bird', 'Early Bird Discount'),
        ('staff_child', 'Staff Child Discount'),
        ('special', 'Special Discount'),
    ]
    
    name = models.CharField(max_length=200)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicable_grade_levels = models.JSONField(default=list)  # List of grade levels
    applicable_fee_types = models.JSONField(default=list)  # List of fee types
    conditions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_until = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fee_discounts'
    
    def __str__(self):
        return f"{self.name} - {self.discount_percentage}%"

class Scholarship(models.Model):
    """Scholarship management"""
    SCHOLARSHIP_TYPE_CHOICES = [
        ('academic', 'Academic Scholarship'),
        ('sports', 'Sports Scholarship'),
        ('arts', 'Arts Scholarship'),
        ('need_based', 'Need-based Scholarship'),
        ('special', 'Special Scholarship'),
    ]
    
    name = models.CharField(max_length=200)
    scholarship_type = models.CharField(max_length=20, choices=SCHOLARSHIP_TYPE_CHOICES)
    description = models.TextField()
    eligibility_criteria = models.TextField()
    scholarship_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    max_scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_slots = models.IntegerField()
    application_deadline = models.DateField()
    academic_year = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scholarships'
    
    def __str__(self):
        return f"{self.name} - {self.scholarship_percentage}%"

class ScholarshipApplication(models.Model):
    """Scholarship applications"""
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scholarship_applications')
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    documents = models.JSONField(default=list)  # List of document URLs
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_scholarships')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'scholarship_applications'
        unique_together = ['scholarship', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.scholarship.name}"

class InstallmentPlan(models.Model):
    """Installment payment plans"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='installment_plans')
    academic_year = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_installments = models.IntegerField()
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'installment_plans'
        unique_together = ['student', 'academic_year']
    
    def __str__(self):
        return f"{self.student.username} - {self.number_of_installments} installments"

class Installment(models.Model):
    """Individual installment records"""
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    payment = models.ForeignKey(FeePayment, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'installments'
        ordering = ['installment_number']
    
    def __str__(self):
        return f"Installment {self.installment_number} - {self.amount}"

class LateFeeConfig(models.Model):
    """Late fee configuration"""
    name = models.CharField(max_length=200)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='late_fee_configs')
    grace_period_days = models.IntegerField(default=0)
    penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fixed_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'late_fee_configs'
    
    def __str__(self):
        return f"{self.name} - {self.penalty_percentage}%"