from django.db import models
from courses.models import Course
from students.models import User

class CourseMaterial(models.Model):
    MATERIAL_TYPES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('link', 'Link'),
        ('other', 'Other'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    folder = models.ForeignKey('MaterialFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='document')
    file = models.FileField(upload_to='course_materials/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_materials')
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'course_materials'
        ordering = ['order', '-upload_date']
        
    def __str__(self):
        return f"{self.course.code} - {self.title}"
    
    def increment_download(self):
        self.download_count += 1
        self.save()

class MaterialFolder(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'material_folders'
        ordering = ['order', 'name']
        verbose_name_plural = 'Material Folders'
        
    def __str__(self):
        return f"{self.course.code} - {self.name}"
