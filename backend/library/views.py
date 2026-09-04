from datetime import timedelta
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permissions import IsAdminUser
from .models import Book, BookCheckout
from .serializers import BookSerializer, BookCheckoutSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]


class BookCheckoutViewSet(viewsets.ModelViewSet):
    queryset = BookCheckout.objects.select_related('book', 'user').all()
    serializer_class = BookCheckoutSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        user = self.request.query_params.get('user')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if user:
            queryset = queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        book = Book.objects.filter(pk=request.data.get('book')).first()
        if not book:
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        if book.available_copies <= 0:
            return Response({'error': f'No copies of "{book.title}" are available right now.'}, status=status.HTTP_400_BAD_REQUEST)

        data = dict(request.data)
        if not data.get('due_date'):
            data['due_date'] = (timezone.now().date() + timedelta(days=14)).isoformat()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(processed_by=request.user)
        book.available_copies -= 1
        book.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        checkout = self.get_object()
        if checkout.status == 'returned':
            return Response({'error': 'This book was already returned.'}, status=status.HTTP_400_BAD_REQUEST)
        checkout.return_date = timezone.now().date()
        checkout.status = 'returned'
        checkout.fine_amount = checkout.calculate_fine()
        checkout.save()
        checkout.book.available_copies += 1
        checkout.book.save()
        return Response(BookCheckoutSerializer(checkout).data)
