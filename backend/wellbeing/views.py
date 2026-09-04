from rest_framework import viewsets
from .models import DailySELCheckIn
from .serializers import DailySELCheckInSerializer

class DailySELCheckInViewSet(viewsets.ModelViewSet):
    queryset = DailySELCheckIn.objects.all()
    serializer_class = DailySELCheckInSerializer