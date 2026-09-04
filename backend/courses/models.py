from django.db import models
from students.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.code} - {self.name}"

class Course(models.Model):
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.PositiveIntegerField(default=3)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    capacity = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['code']
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='enrolled').count()
    
    @property
    def available_seats(self):
        return self.capacity - self.enrolled_count

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('failed', 'Failed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(blank=True, null=True)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course', 'semester', 'academic_year']
        ordering = ['-enrollment_date']
        
    def __str__(self):
        return f"{self.student.username} - {self.course.code} ({self.status})"

class Grade(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    midterm_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assignment_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overall_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    letter_grade = models.CharField(max_length=2, null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_grades')
    graded_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grades'
        
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.code}: {self.overall_grade or 'N/A'}"
    
    def calculate_overall_grade(self):
        if self.midterm_grade and self.final_grade and self.assignment_grade:
            # Weighted average: 30% midterm, 40% final, 30% assignments
            self.overall_grade = (
                self.midterm_grade * 0.3 + 
                self.final_grade * 0.4 + 
                self.assignment_grade * 0.3
            )
            self.letter_grade = self.get_letter_grade(self.overall_grade)
            self.save()
    
    def get_letter_grade(self, numeric_grade):
        if numeric_grade >= 90:
            return 'A'
        elif numeric_grade >= 80:
            return 'B'
        elif numeric_grade >= 70:
            return 'C'
        elif numeric_grade >= 60:
            return 'D'
        else:
            return 'F'
