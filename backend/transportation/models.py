from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class BusRoute(models.Model):
    """Bus route definition"""
    route_number = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=200)
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Distance in km")
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bus_routes'
        ordering = ['route_number']
    
    def __str__(self):
        return f"{self.route_number} - {self.route_name}"

class BusStop(models.Model):
    """Bus stop definitions"""
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=200)
    stop_number = models.IntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_geofence_radius = models.IntegerField(default=100, help_text="Radius in meters")
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'bus_stops'
        ordering = ['stop_number']
        unique_together = ['route', 'stop_number']
    
    def __str__(self):
        return f"{self.route.route_number} - Stop {self.stop_number}: {self.stop_name}"

class Bus(models.Model):
    """Bus information"""
    BUS_STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]
    
    bus_number = models.CharField(max_length=20, unique=True)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(0)])
    route = models.ForeignKey(BusRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')
    status = models.CharField(max_length=20, choices=BUS_STATUS_CHOICES, default='active')
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)
    gps_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buses'
        ordering = ['bus_number']
    
    def __str__(self):
        return f"{self.bus_number} - {self.license_plate}"

class Driver(models.Model):
    """Bus driver profiles"""
    LICENSE_STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry_date = models.DateField()
    license_status = models.CharField(max_length=20, choices=LICENSE_STATUS_CHOICES, default='valid')
    assigned_bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    experience_years = models.IntegerField(default=0)
    phone = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20)
    police_clearance_expiry = models.DateField(null=True, blank=True)
    medical_clearance_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drivers'
    
    def __str__(self):
        return f"{self.user.username} - {self.license_number}"

class Attendant(models.Model):
    """Bus attendant profiles"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendant_profile')
    assigned_bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendants')
    phone = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20)
    police_clearance_expiry = models.DateField(null=True, blank=True)
    medical_clearance_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendants'
    
    def __str__(self):
        return f"{self.user.username}"

class StudentBusAssignment(models.Model):
    """Student to bus assignment"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bus_assignments')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='student_assignments')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='pickup_students')
    dropoff_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='dropoff_students')
    academic_year = models.CharField(max_length=10)
    card_number = models.CharField(max_length=50, unique=True, blank=True)
    card_type = models.CharField(max_length=20, choices=[('rfid', 'RFID'), ('barcode', 'Barcode'), ('qr', 'QR Code')], default='rfid')
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_bus_assignments'
        unique_together = ['student', 'academic_year']
    
    def __str__(self):
        return f"{self.student.username} - Bus {self.bus.bus_number}"

class BusLocation(models.Model):
    """Real-time bus location tracking"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    heading = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bus_locations'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.timestamp}"

class BusMaintenance(models.Model):
    """Bus maintenance records"""
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('emergency', 'Emergency Repair'),
    ]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_date = models.DateField()
    completed_by = models.CharField(max_length=200)
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bus_maintenance'
        ordering = ['-maintenance_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.maintenance_type}"

class BusFuelExpense(models.Model):
    """Bus fuel expense logging"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='fuel_expenses')
    fuel_date = models.DateField()
    fuel_type = models.CharField(max_length=20, choices=[('diesel', 'Diesel'), ('petrol', 'Petrol'), ('cng', 'CNG'), ('electric', 'Electric')])
    quantity_liters = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    odometer_reading = models.IntegerField()
    fuel_station = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bus_fuel_expenses'
        ordering = ['-fuel_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.fuel_date}"