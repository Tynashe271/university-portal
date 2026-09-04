from django.db import models
from courses.models import Course
from students.models import User

class Forum(models.Model):
    FORUM_TYPES = [
        ('general', 'General Discussion'),
        ('course', 'Course Specific'),
        ('assignment', 'Assignment Help'),
        ('technical', 'Technical Support'),
        ('social', 'Social'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    forum_type = models.CharField(max_length=20, choices=FORUM_TYPES, default='general')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forums')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'forums'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.forum_type})"
    
    @property
    def thread_count(self):
        return self.threads.count()

class Thread(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'forum_threads'
        ordering = ['-is_pinned', '-updated_at']
        
    def __str__(self):
        return f"{self.title}"
    
    @property
    def reply_count(self):
        return self.replies.count()
    
    @property
    def last_reply(self):
        return self.replies.order_by('-created_at').first()

class Reply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='forum_replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'forum_replies'
        ordering = ['created_at']
        
    def __str__(self):
        return f"Reply by {self.author.username if self.author else 'Unknown'}"

class ForumLike(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_likes'
        unique_together = ['thread', 'user']
        
    def __str__(self):
        return f"{self.user.username} likes {self.thread.title}"

class ForumSubscription(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='subscribers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_subscriptions')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    notify_on_new_thread = models.BooleanField(default=True)
    notify_on_reply = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'forum_subscriptions'
        unique_together = ['forum', 'user']
        
    def __str__(self):
        return f"{self.user.username} subscribed to {self.forum.name}"
