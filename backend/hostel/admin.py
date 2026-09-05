from django.contrib import admin
from .models import Hostel, Room, Bed, BoardingAllocation, LeaveRequest, RollCall, RollCallRecord, Visitor

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostel_type', 'warden', 'is_active']
    list_filter = ['hostel_type', 'is_active']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'room_number', 'floor', 'capacity']
    list_filter = ['hostel']

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['room', 'bed_number', 'status']
    list_filter = ['status']

@admin.register(BoardingAllocation)
class BoardingAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'bed', 'academic_year', 'status', 'date_allocated']
    list_filter = ['status', 'academic_year']
    search_fields = ['student__username']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'date_from', 'date_to', 'status']
    list_filter = ['status']
    search_fields = ['student__username']

@admin.register(RollCall)
class RollCallAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'date', 'session', 'taken_by']
    list_filter = ['hostel', 'session']

@admin.register(RollCallRecord)
class RollCallRecordAdmin(admin.ModelAdmin):
    list_display = ['roll_call', 'student', 'present']
    list_filter = ['present']

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['student', 'visitor_name', 'visit_date', 'time_in', 'time_out']
    search_fields = ['student__username', 'visitor_name']
