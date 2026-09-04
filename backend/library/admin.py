from django.contrib import admin
from .models import Book, BookCheckout, BookReservation, ReadingAnalytics, LibraryTransaction

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies']
    list_filter = ['genre']
    search_fields = ['title', 'author', 'isbn']

@admin.register(BookCheckout)
class BookCheckoutAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'checkout_date', 'due_date', 'status', 'fine_amount']
    list_filter = ['status']
    search_fields = ['book__title', 'user__username']

@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'reservation_date', 'expiry_date', 'is_active']
    list_filter = ['is_active']

@admin.register(ReadingAnalytics)
class ReadingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_books_read', 'total_pages_read', 'average_reading_time']
    search_fields = ['user__username']

@admin.register(LibraryTransaction)
class LibraryTransactionAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'transaction_type', 'transaction_date', 'amount']
    list_filter = ['transaction_type']