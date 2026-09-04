from rest_framework import viewsets
from .models import FeeStructure, FeeAccount, FeePayment
from .serializers import FeeStructureSerializer, FeeAccountSerializer, FeePaymentSerializer

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

class FeeAccountViewSet(viewsets.ModelViewSet):
    queryset = FeeAccount.objects.all()
    serializer_class = FeeAccountSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_student():
            return FeeAccount.objects.filter(student=user)
        return FeeAccount.objects.all()

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer