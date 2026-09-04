from django.db.models import Sum
from rest_framework import permissions, viewsets
from config.permissions import IsAdminUser
from .models import FeeStructure, FeeAccount, FeePayment
from .serializers import FeeStructureSerializer, FeeAccountSerializer, FeePaymentSerializer


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        grade_level = self.request.query_params.get('grade_level')
        academic_year = self.request.query_params.get('academic_year')
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        return queryset


class FeeAccountViewSet(viewsets.ModelViewSet):
    """A student can view their own fee account (used by the student
    portal's Fees tab); only admin/bursar staff can create or change one."""
    queryset = FeeAccount.objects.all()
    serializer_class = FeeAccountSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_student():
            return FeeAccount.objects.filter(student=user)
        return FeeAccount.objects.all()

    def perform_create(self, serializer):
        account = serializer.save()
        account.fees_due = account.calculate_due()
        account.save()

    def perform_update(self, serializer):
        account = serializer.save()
        account.fees_due = account.calculate_due()
        account.save()


class FeePaymentViewSet(viewsets.ModelViewSet):
    """Same split as FeeAccount — a student can see their own payment
    history and receipts; only admin/bursar staff can record a payment."""
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_student():
            return FeePayment.objects.filter(fee_account__student=user)
        return FeePayment.objects.all()

    def perform_create(self, serializer):
        payment = serializer.save(processed_by=self.request.user, status='completed')
        # Keep the account's running totals in sync with what's actually
        # been paid, so the student portal's balance is always accurate.
        account = payment.fee_account
        account.fees_paid = account.payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        account.fees_due = account.calculate_due()
        account.save()
