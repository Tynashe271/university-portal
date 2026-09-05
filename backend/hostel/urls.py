from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet, RoomViewSet, BedViewSet, BoardingAllocationViewSet,
    LeaveRequestViewSet, RollCallViewSet, VisitorViewSet,
)

router = DefaultRouter()
router.register(r'hostels', HostelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'beds', BedViewSet)
router.register(r'allocations', BoardingAllocationViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'roll-calls', RollCallViewSet)
router.register(r'visitors', VisitorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
