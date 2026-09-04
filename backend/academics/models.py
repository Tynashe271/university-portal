from django.conf import settings
from django.db import models

# Reuse the same grade/academic-year choices as admissions, so a Classroom's
# grade always lines up with what an application was accepted into.
from admissions.models import AdmissionApplication


class Department(models.Model):
    """A subject grouping, e.g. Sciences, Languages, Humanities."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True)

    class Meta:
        db_table = 'academic_departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    compulsory = models.BooleanField(default=False, help_text="Taken by every student, regardless of grade")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['name']

    def __str__(self):
        return self.name


class Term(models.Model):
    TERM_CHOICES = [('1', 'Term 1'), ('2', 'Term 2'), ('3', 'Term 3')]

    academic_year = models.CharField(max_length=10, choices=AdmissionApplication.ACADEMIC_YEAR_CHOICES)
    term = models.CharField(max_length=1, choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = 'academic_terms'
        unique_together = ['academic_year', 'term']
        ordering = ['academic_year', 'term']

    def __str__(self):
        return f"{self.get_term_display()} {self.academic_year}"


class Classroom(models.Model):
    """A physical class/stream a group of students sit in for a grade and
    academic year — e.g. "1-2" (Form 1, stream 2). This is the same
    grade/stream shape admissions.classing.py already assigns Form 1
    applicants into; defining it here lets the school pre-set capacity and
    a class teacher instead of relying on the hardcoded 40-per-class limit.
    """
    grade = models.CharField(max_length=10, choices=AdmissionApplication.GRADE_LEVEL_CHOICES)
    stream = models.PositiveIntegerField(default=1, help_text="1, 2, 3... — which stream within the grade")
    academic_year = models.CharField(max_length=10, choices=AdmissionApplication.ACADEMIC_YEAR_CHOICES)
    room = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=40)
    class_teacher = models.ForeignKey(
        'staff.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='classes_led'
    )

    class Meta:
        db_table = 'classrooms'
        unique_together = ['grade', 'stream', 'academic_year']
        ordering = ['grade', 'stream']

    @property
    def name(self):
        grade_number = {'form1': '1', 'form2': '2', 'form3': '3', 'form4': '4', 'lower6': 'L6', 'upper6': 'U6'}
        return f"{grade_number.get(self.grade, self.grade)}-{self.stream}"

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
