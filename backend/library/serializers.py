from rest_framework import serializers
from .models import Book, BookCheckout

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['available_copies']


class BookCheckoutSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = BookCheckout
        fields = '__all__'
        read_only_fields = ['checkout_date', 'return_date', 'status', 'fine_amount', 'processed_by']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
