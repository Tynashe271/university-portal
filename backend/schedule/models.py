from django.db import models
from courses.models import Course
from students.models import User

class TimeSlot(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'time_slots'
        ordering = ['day', 'start_time']
        unique_together = ['day', 'start_time', 'end_time']
        
    def __str__(self):
        return f"{self.get_day_display()} {self.start_time} - {self.end_time}"

class Schedule(models.Model):
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    room = models.CharField(max_length=50, blank=True, null=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=10)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_schedules')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        ordering = ['academic_year', 'semester', 'time_slot']
        unique_together = ['course', 'time_slot', 'semester', 'academic_year']
        
    def __str__(self):
        return f"{self.course.code} - {self.time_slot} ({self.semester} {self.academic_year})"

class Timetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetables')
    semester = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=10)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'timetables'
        unique_together = ['user', 'semester', 'academic_year']
        ordering = ['-academic_year', '-semester']
        
    def __str__(self):
        return f"{self.user.username} - {self.semester} {self.academic_year}"

class ClassConflict(models.Model):
    schedule1 = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='conflicts_as_first')
    schedule2 = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='conflicts_as_second')
    conflict_type = models.CharField(max_length=20)  # 'time', 'room', 'instructor'
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'class_conflicts'
        unique_together = ['schedule1', 'schedule2', 'conflict_type']
        
    def __str__(self):
        return f"Conflict: {self.schedule1.course.code} vs {self.schedule2.course.code}"
