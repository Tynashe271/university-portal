from django.contrib import admin
from .models import DailySELCheckIn, CounselingSession, IncidentReport, WellnessTrend, BehavioralReward, PositiveBehaviorLog

@admin.register(DailySELCheckIn)
class DailySELCheckInAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'mood', 'sleep_quality', 'energy_level']
    list_filter = ['mood', 'sleep_quality', 'energy_level']
    search_fields = ['student__username']

@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'counselor', 'session_type', 'scheduled_date', 'status', 'risk_level']
    list_filter = ['session_type', 'status', 'risk_level']
    search_fields = ['student__username', 'counselor__username']

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['incident_type', 'incident_date', 'location', 'severity', 'status']
    list_filter = ['incident_type', 'severity', 'status']
    search_fields = ['location', 'description']

@admin.register(WellnessTrend)
class WellnessTrendAdmin(admin.ModelAdmin):
    list_display = ['student', 'analysis_period', 'risk_level', 'flagged_for_review']
    list_filter = ['risk_level', 'flagged_for_review']
    search_fields = ['student__username']

@admin.register(BehavioralReward)
class BehavioralRewardAdmin(admin.ModelAdmin):
    list_display = ['student', 'reward_type', 'points', 'category', 'awarded_date']
    list_filter = ['reward_type', 'category']
    search_fields = ['student__username']

@admin.register(PositiveBehaviorLog)
class PositiveBehaviorLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'behavior', 'category', 'date', 'points_awarded']
    list_filter = ['category']
    search_fields = ['student__username', 'behavior']