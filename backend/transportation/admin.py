from django.contrib import admin
from .models import BusRoute, BusStop, Bus, Driver, Attendant, StudentBusAssignment, BusLocation, BusMaintenance, BusFuelExpense

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'route_name', 'start_point', 'end_point', 'is_active']
    list_filter = ['is_active']
    search_fields = ['route_number', 'route_name']

@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'stop_number', 'stop_name', 'arrival_time', 'departure_time']
    list_filter = ['route']

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['bus_number', 'license_plate', 'capacity', 'route', 'status']
    list_filter = ['status']
    search_fields = ['bus_number', 'license_plate']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'license_status', 'assigned_bus']
    list_filter = ['license_status']
    search_fields = ['user__username', 'license_number']

@admin.register(Attendant)
class AttendantAdmin(admin.ModelAdmin):
    list_display = ['user', 'assigned_bus', 'phone']
    search_fields = ['user__username']

@admin.register(StudentBusAssignment)
class StudentBusAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'bus', 'pickup_stop', 'dropoff_stop', 'is_active']
    list_filter = ['is_active']
    search_fields = ['student__username']

@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ['bus', 'latitude', 'longitude', 'timestamp']
    list_filter = ['bus']

@admin.register(BusMaintenance)
class BusMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['bus', 'maintenance_type', 'maintenance_date', 'cost']
    list_filter = ['maintenance_type']

@admin.register(BusFuelExpense)
class BusFuelExpenseAdmin(admin.ModelAdmin):
    list_display = ['bus', 'fuel_date', 'fuel_type', 'quantity_liters', 'total_cost']
    list_filter = ['fuel_type']