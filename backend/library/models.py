from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

class Book(models.Model):
    """Library book catalog"""
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('mathematics', 'Mathematics'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('technology', 'Technology'),
        ('literature', 'Literature'),
        ('children', 'Children'),
        ('reference', 'Reference'),
        ('other', 'Other'),
    ]
    
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    total_copies = models.IntegerField(validators=[MinValueValidator(0)])
    available_copies = models.IntegerField(validators=[MinValueValidator(0)])
    location = models.CharField(max_length=100)  # Shelf location
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/covers/', blank=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='books/qrcodes/', blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'library_books'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        # Default available_copies to total_copies on first creation only.
        # The old `if not self.available_copies` check used zero as a proxy
        # for "unset", which silently reset a fully-checked-out book (0
        # available, a legitimate value) back to full stock on every save —
        # verified this let checkouts succeed with no copies left at all.
        if self.pk is None and self.available_copies is None:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

class BookCheckout(models.Model):
    """Book checkout/check-in records"""
    STATUS_CHOICES = [
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='checkouts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_checkouts')
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_out')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_checkouts')
    
    class Meta:
        db_table = 'book_checkouts'
        ordering = ['-checkout_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
    
    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            from datetime import timedelta
            days_overdue = (self.return_date - self.due_date).days
            fine_per_day = 1.00  # $1 per day
            return days_overdue * fine_per_day
        return 0

class BookReservation(models.Model):
    """Book reservation/hold system"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notification_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'book_reservations'
        unique_together = ['book', 'user']
        ordering = ['reservation_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.user.username}"

class ReadingAnalytics(models.Model):
    """Reading habit analytics"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_analytics')
    total_books_read = models.IntegerField(default=0)
    total_pages_read = models.IntegerField(default=0)
    favorite_genres = models.JSONField(default=list)
    reading_frequency = models.JSONField(default=dict)  # Monthly reading stats
    average_reading_time = models.IntegerField(default=0)  # in minutes
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reading_analytics'
    
    def __str__(self):
        return f"{self.user.username} - {self.total_books_read} books"

class LibraryTransaction(models.Model):
    """Library transactions for reporting"""
    TRANSACTION_TYPE_CHOICES = [
        ('checkout', 'Checkout'),
        ('return', 'Return'),
        ('renewal', 'Renewal'),
        ('fine_payment', 'Fine Payment'),
        ('loss_report', 'Loss Report'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'library_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.book.title}"