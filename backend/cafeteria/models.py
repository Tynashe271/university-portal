from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class MenuItem(models.Model):
    """Cafeteria menu items"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    ]
    
    CATEGORY_CHOICES = [
        ('main_course', 'Main Course'),
        ('side_dish', 'Side Dish'),
        ('beverage', 'Beverage'),
        ('dessert', 'Dessert'),
        ('fruit', 'Fruit'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    calories = models.IntegerField(null=True, blank=True)
    protein = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in grams
    carbs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in grams
    fat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in grams
    allergens = models.JSONField(default=list)  # List of allergens
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='cafeteria/menu/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.meal_type}"

class DailyMenu(models.Model):
    """Daily menu display"""
    date = models.DateField()
    breakfast_items = models.ManyToManyField(MenuItem, related_name='breakfast_menus')
    lunch_items = models.ManyToManyField(MenuItem, related_name='lunch_menus')
    snack_items = models.ManyToManyField(MenuItem, related_name='snack_menus')
    dinner_items = models.ManyToManyField(MenuItem, related_name='dinner_menus')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_menus'
        unique_together = ['date']
    
    def __str__(self):
        return f"Menu for {self.date}"

class StudentMealSelection(models.Model):
    """Student meal selection"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_selections')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    selected_items = models.ManyToManyField(MenuItem, related_name='student_selections')
    allergen_alert = models.BooleanField(default=False)
    special_notes = models.TextField(blank=True)
    selected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_meal_selections'
        unique_together = ['student', 'date', 'meal_type']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.meal_type}"

class ParentWallet(models.Model):
    """Parent wallet for cashless payments"""
    parent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cafeteria_wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    auto_recharge_enabled = models.BooleanField(default=False)
    auto_recharge_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    low_balance_threshold = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parent_wallets'
    
    def __str__(self):
        return f"{self.parent.username} - Balance: {self.balance}"

class WalletTransaction(models.Model):
    """Wallet transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('recharge', 'Recharge'),
        ('meal_payment', 'Meal Payment'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
    ]
    
    wallet = models.ForeignKey(ParentWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    related_student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='wallet_transactions')
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.wallet.parent.username} - {self.transaction_type} - {self.amount}"

class MealConsumption(models.Model):
    """Daily consumption tracking"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_consumptions')
    date = models.DateField()
    meals_consumed = models.JSONField(default=dict)  # {"breakfast": true, "lunch": true}
    total_calories = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=[('wallet', 'Wallet'), ('cash', 'Cash'), ('subsidized', 'Subsidized')], default='wallet')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'meal_consumptions'
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date}"

class FoodInventory(models.Model):
    """Food stock management"""
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=[('kg', 'Kilograms'), ('liters', 'Liters'), ('pieces', 'Pieces'), ('packs', 'Packs')])
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200, blank=True)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    storage_location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'food_inventory'
        ordering = ['item_name']
    
    def __str__(self):
        return f"{self.item_name} - {self.current_stock} {self.unit}"

class MonthlyMealBilling(models.Model):
    """Monthly meal billing for parents"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monthly_meal_bills')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children_meal_bills')
    billing_month = models.CharField(max_length=20)  # e.g., "January 2024"
    total_meals = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subsidy_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'monthly_meal_billing'
        unique_together = ['student', 'billing_month']
        ordering = ['-billing_month']
    
    def __str__(self):
        return f"{self.student.username} - {self.billing_month} - {self.final_amount}"