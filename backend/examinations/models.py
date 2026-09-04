from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class QuestionBank(models.Model):
    """Question bank with topic/chapter tagging"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('english', 'English'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('computer_science', 'Computer Science'),
        ('other', 'Other'),
    ]
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    chapter = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    marks = models.IntegerField(validators=[MinValueValidator(0)])
    options = models.JSONField(default=list)  # For multiple choice
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_bank'
        ordering = ['subject', 'chapter', 'topic']
    
    def __str__(self):
        return f"{self.subject} - {self.question_text[:50]}"

class ExamPaper(models.Model):
    """Exam paper generation"""
    EXAM_TYPE_CHOICES = [
        ('unit_test', 'Unit Test'),
        ('mid_term', 'Mid Term'),
        ('final', 'Final Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    
    PAPER_TYPE_CHOICES = [
        ('randomized', 'Randomized'),
        ('fixed', 'Fixed'),
    ]
    
    exam_name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    subject = models.CharField(max_length=20)
    grade_level = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=10)
    total_marks = models.IntegerField()
    duration_minutes = models.IntegerField()
    paper_type = models.CharField(max_length=20, choices=PAPER_TYPE_CHOICES, default='fixed')
    question_count = models.IntegerField()
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exam_papers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.exam_name} - {self.subject}"

class ExamQuestion(models.Model):
    """Questions assigned to exam papers"""
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='questions')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='exam_assignments')
    question_number = models.IntegerField()
    marks = models.IntegerField()
    
    class Meta:
        db_table = 'exam_questions'
        ordering = ['question_number']
        unique_together = ['exam_paper', 'question_number']
    
    def __str__(self):
        return f"{self.exam_paper.exam_name} - Q{self.question_number}"

class ExamSchedule(models.Model):
    """Exam timetable creation"""
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='schedules')
    exam_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    invigilator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='invigilated_exams')
    grade_level = models.CharField(max_length=10)
    section = models.CharField(max_length=10, blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exam_schedules'
        ordering = ['exam_date']
    
    def __str__(self):
        return f"{self.exam_paper.exam_name} - {self.exam_date}"

class StudentExamResult(models.Model):
    """Student exam results"""
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    total_marks = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    percentile = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_exam_results'
        unique_together = ['exam_schedule', 'student']
        ordering = ['-exam_schedule__exam_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam_schedule.exam_paper.exam_name}"

class ReEvaluationRequest(models.Model):
    """Re-evaluation and re-test request workflow"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    exam_result = models.ForeignKey(StudentExamResult, on_delete=models.CASCADE, related_name='re_evaluation_requests')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='re_evaluation_requests')
    reason = models.TextField()
    requested_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_re_evaluations')
    review_date = models.DateTimeField(null=True, blank=True)
    original_marks = models.DecimalField(max_digits=6, decimal_places=2)
    revised_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fee_paid = models.BooleanField(default=False)
    
    class Meta:
        db_table = 're_evaluation_requests'
        ordering = ['-requested_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam_result.exam_schedule.exam_paper.exam_name}"

class OnlineExam(models.Model):
    """Online examination portal"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    PROCTORING_CHOICES = [
        ('none', 'No Proctoring'),
        ('auto', 'Auto Proctoring'),
        ('live', 'Live Proctoring'),
    ]
    
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='online_exams')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    proctoring_type = models.CharField(max_length=20, choices=PROCTORING_CHOICES, default='none')
    max_attempts = models.IntegerField(default=1)
    password = models.CharField(max_length=50, blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'online_exams'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.exam_paper.exam_name} - {self.start_time}"

class OnlineExamAttempt(models.Model):
    """Student online exam attempts"""
    online_exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='online_exam_attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    answers = models.JSONField(default=dict)  # Question ID: Answer
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    is_submitted = models.BooleanField(default=False)
    proctoring_logs = models.JSONField(default=list)  # Proctoring events
    
    class Meta:
        db_table = 'online_exam_attempts'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.student.username} - {self.online_exam.exam_paper.exam_name}"


class Assessment(models.Model):
    """A test/assignment/exam given to a whole class in a subject — the
    unit marks are recorded against. Built fresh rather than reusing
    QuestionBank/ExamPaper above (a full online-exam authoring system with
    its own hardcoded subject list, unrelated to academics.Subject)."""
    ASSESSMENT_TYPE_CHOICES = [
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
    ]

    name = models.CharField(max_length=200)
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='assessments')
    classroom = models.ForeignKey('academics.Classroom', on_delete=models.CASCADE, related_name='assessments')
    term = models.ForeignKey('academics.Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES, default='test')
    max_score = models.PositiveIntegerField(default=100)
    date = models.DateField()
    published = models.BooleanField(default=False, help_text="Whether results are released (for a future student/parent results view)")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assessments'
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} · {self.classroom.name} · {self.subject.name}"


class Mark(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marks')
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    comments = models.CharField(max_length=300, blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='marks_graded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marks'
        unique_together = ['assessment', 'student']
        ordering = ['-score']

    @property
    def percentage(self):
        return round(float(self.score) / float(self.assessment.max_score) * 100, 1) if self.assessment.max_score else None

    @property
    def letter_grade(self):
        pct = self.percentage
        if pct is None:
            return None
        if pct >= 80:
            return 'A'
        if pct >= 70:
            return 'B'
        if pct >= 60:
            return 'C'
        if pct >= 50:
            return 'D'
        return 'F'

    def __str__(self):
        return f"{self.student.username} - {self.assessment.name}: {self.score}"