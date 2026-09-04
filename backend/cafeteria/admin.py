from django.contrib import admin
from .models import MenuItem, DailyMenu, StudentMealSelection, ParentWallet, WalletTransaction, MealConsumption, FoodInventory, MonthlyMealBilling

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'category', 'price', 'is_available']
    list_filter = ['meal_type', 'category', 'is_available']
    search_fields = ['name']

@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ['date', 'is_published']
    list_filter = ['is_published']

@admin.register(StudentMealSelection)
class StudentMealSelectionAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'meal_type', 'allergen_alert']
    list_filter = ['meal_type', 'allergen_alert']
    search_fields = ['student__username']

@admin.register(ParentWallet)
class ParentWalletAdmin(admin.ModelAdmin):
    list_display = ['parent', 'balance', 'auto_recharge_enabled', 'low_balance_threshold']
    search_fields = ['parent__username']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'transaction_date']
    list_filter = ['transaction_type']

@admin.register(MealConsumption)
class MealConsumptionAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'total_calories', 'total_cost', 'payment_method']
    search_fields = ['student__username']

@admin.register(FoodInventory)
class FoodInventoryAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'current_stock', 'unit', 'unit_cost']
    search_fields = ['item_name']

@admin.register(MonthlyMealBilling)
class MonthlyMealBillingAdmin(admin.ModelAdmin):
    list_display = ['student', 'parent', 'billing_month', 'total_cost', 'paid']
    list_filter = ['paid', 'billing_month']
    search_fields = ['student__username']