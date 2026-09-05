from django.db import models
from django.conf import settings


class Hostel(models.Model):
    """A boarding house — e.g. 'Baobab House' (boys) or 'Acacia House' (girls)."""
    HOSTEL_TYPE_CHOICES = [
        ('boys', 'Boys'),
        ('girls', 'Girls'),
        ('mixed', 'Mixed'),
    ]

    name = models.CharField(max_length=100, unique=True)
    hostel_type = models.CharField(max_length=10, choices=HOSTEL_TYPE_CHOICES)
    warden = models.ForeignKey(
        'staff.StaffProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='hostels_managed'
    )
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hostels'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=4, help_text="Number of beds in the room")

    class Meta:
        db_table = 'hostel_rooms'
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'room_number']

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"


class Bed(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under maintenance'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        db_table = 'hostel_beds'
        unique_together = ['room', 'bed_number']
        ordering = ['room', 'bed_number']

    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"


class BoardingAllocation(models.Model):
    """Which bed a boarding student occupies for a given academic year/term."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('vacated', 'Vacated'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boarding_allocations')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='allocations')
    academic_year = models.CharField(max_length=10)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    date_allocated = models.DateField(auto_now_add=True)
    date_vacated = models.DateField(null=True, blank=True)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')

    class Meta:
        db_table = 'boarding_allocations'
        ordering = ['-date_allocated']

    def __str__(self):
        return f"{self.student.username} - {self.bed}"


class LeaveRequest(models.Model):
    """A boarding student's request to leave the hostel for a period."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hostel_leave_requests')
    date_from = models.DateField()
    date_to = models.DateField()
    destination = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'hostel_leave_requests'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.student.username} - {self.date_from} to {self.date_to}"


class RollCall(models.Model):
    SESSION_CHOICES = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='roll_calls')
    date = models.DateField()
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hostel_roll_calls'
        unique_together = ['hostel', 'date', 'session']
        ordering = ['-date']

    def __str__(self):
        return f"{self.hostel.name} - {self.date} {self.session}"


class RollCallRecord(models.Model):
    roll_call = models.ForeignKey(RollCall, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hostel_roll_call_records')
    present = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'hostel_roll_call_records'
        unique_together = ['roll_call', 'student']

    def __str__(self):
        return f"{self.roll_call} - {self.student.username}"


class Visitor(models.Model):
    """A visitor who came to see a boarding student."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hostel_visitors')
    visitor_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100, blank=True)
    visit_date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    purpose = models.CharField(max_length=300, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')

    class Meta:
        db_table = 'hostel_visitors'
        ordering = ['-visit_date', '-time_in']

    def __str__(self):
        return f"{self.visitor_name} visiting {self.student.username}"
