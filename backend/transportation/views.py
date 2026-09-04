from rest_framework import viewsets
from .models import BusRoute
from .serializers import BusRouteSerializer

class BusRouteViewSet(viewsets.ModelViewSet):
    queryset = BusRoute.objects.all()
    serializer_class = BusRouteSerializer