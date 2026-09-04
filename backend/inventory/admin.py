from django.contrib import admin
from .models import Asset, AssetCheckout, MaintenanceRequest, ConsumableInventory, ConsumableTransaction, AssetUsageAnalytics

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'name', 'asset_type', 'status', 'location', 'assigned_to']
    list_filter = ['asset_type', 'status']
    search_fields = ['asset_code', 'name']

@admin.register(AssetCheckout)
class AssetCheckoutAdmin(admin.ModelAdmin):
    list_display = ['asset', 'user', 'checkout_date', 'expected_return_date', 'status']
    list_filter = ['status']
    search_fields = ['asset__name', 'user__username']

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['asset', 'reported_by', 'priority', 'status', 'reported_date']
    list_filter = ['priority', 'status']
    search_fields = ['asset__name', 'reported_by__username']

@admin.register(ConsumableInventory)
class ConsumableInventoryAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'unit', 'current_stock', 'minimum_stock', 'unit_cost']
    search_fields = ['item_name']

@admin.register(ConsumableTransaction)
class ConsumableTransactionAdmin(admin.ModelAdmin):
    list_display = ['consumable', 'transaction_type', 'quantity', 'transaction_date']
    list_filter = ['transaction_type']

@admin.register(AssetUsageAnalytics)
class AssetUsageAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['asset', 'usage_hours', 'failure_prediction', 'last_updated']
    list_filter = ['failure_prediction']