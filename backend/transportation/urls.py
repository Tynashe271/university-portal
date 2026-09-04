from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusRouteViewSet, BusStopViewSet, BusViewSet, DriverViewSet, StudentBusAssignmentViewSet

router = DefaultRouter()
router.register(r'routes', BusRouteViewSet)
router.register(r'stops', BusStopViewSet)
router.register(r'buses', BusViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'assignments', StudentBusAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]