from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Asset(models.Model):
    """School assets with QR code tracking"""
    ASSET_TYPE_CHOICES = [
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('laboratory', 'Laboratory Equipment'),
        ('sports', 'Sports Equipment'),
        ('stationery', 'Stationery'),
        ('books', 'Books'),
        ('consumables', 'Consumables'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
        ('disposed', 'Disposed'),
    ]
    
    asset_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='assets/qrcodes/', blank=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    assigned_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assets'
        ordering = ['asset_code']
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"

class AssetCheckout(models.Model):
    """Asset check-in/check-out system"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='checkouts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asset_checkouts')
    checkout_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('checked_out', 'Checked Out'), ('returned', 'Returned'), ('overdue', 'Overdue')], default='checked_out')
    condition_on_checkout = models.TextField(blank=True)
    condition_on_return = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_asset_checkouts')
    
    class Meta:
        db_table = 'asset_checkouts'
        ordering = ['-checkout_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.user.username}"

class MaintenanceRequest(models.Model):
    """Maintenance request ticketing"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_requests')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_maintenance')
    issue_description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_maintenance')
    reported_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'maintenance_requests'
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.status}"

class ConsumableInventory(models.Model):
    """Consumable inventory tracking"""
    UNIT_CHOICES = [
        ('pieces', 'Pieces'),
        ('kg', 'Kilograms'),
        ('liters', 'Liters'),
        ('boxes', 'Boxes'),
        ('packs', 'Packs'),
        ('reams', 'Reams'),
    ]
    
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    maximum_stock = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    reorder_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_restocked = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consumable_inventory'
        ordering = ['item_name']
    
    def __str__(self):
        return f"{self.item_name} - {self.current_stock} {self.unit}"
    
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

class ConsumableTransaction(models.Model):
    """Consumable stock transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
    ]
    
    consumable = models.ForeignKey(ConsumableInventory, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='consumable_transactions')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'consumable_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.consumable.item_name} - {self.transaction_type}"

class AssetUsageAnalytics(models.Model):
    """Asset usage analytics for predictive maintenance"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='usage_analytics')
    usage_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_usage_date = models.DateTimeField(auto_now=True)
    usage_frequency = models.IntegerField(default=0)  # Times used per month
    average_usage_duration = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # In hours
    maintenance_count = models.IntegerField(default=0)
    failure_prediction = models.CharField(max_length=20, choices=[('low', 'Low Risk'), ('medium', 'Medium Risk'), ('high', 'High Risk')], default='low')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asset_usage_analytics'
    
    def __str__(self):
        return f"{self.asset.name} - {self.usage_hours} hours"