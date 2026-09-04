from django.contrib import admin
from .models import ParentProfile, StudentParentRelation, Message, ConferenceSchedule, ParentNotification, DailySummary, FeedbackForm, FeedbackResponse, AnnouncementReadReceipt

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'occupation', 'receives_sms', 'receives_email']
    list_filter = ['relationship', 'receives_sms', 'receives_email']
    search_fields = ['user__username']

@admin.register(StudentParentRelation)
class StudentParentRelationAdmin(admin.ModelAdmin):
    list_display = ['student', 'parent', 'relationship', 'is_primary_contact', 'pickup_permission']
    list_filter = ['relationship', 'is_primary_contact', 'pickup_permission']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'message_type', 'sent_at', 'is_read']
    list_filter = ['message_type', 'priority', 'is_read']
    search_fields = ['subject', 'sender__username', 'recipient__username']

@admin.register(ConferenceSchedule)
class ConferenceScheduleAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'parent', 'scheduled_date', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['student__username', 'teacher__username', 'parent__username']

@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'created_at', 'is_read']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'recipient__username']

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'attendance_status', 'mood', 'homework_completed']
    list_filter = ['attendance_status', 'mood', 'homework_completed']
    search_fields = ['student__username']

@admin.register(FeedbackForm)
class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'feedback_type', 'is_active', 'start_date', 'end_date']
    list_filter = ['feedback_type', 'is_active']

@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['feedback_form', 'parent', 'submitted_at', 'is_anonymous']
    list_filter = ['is_anonymous']

@admin.register(AnnouncementReadReceipt)
class AnnouncementReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'read_at']
    search_fields = ['user__username']