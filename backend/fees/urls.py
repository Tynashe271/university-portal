from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, FeeAccountViewSet, FeePaymentViewSet

router = DefaultRouter()
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'fee-accounts', FeeAccountViewSet)
router.register(r'fee-payments', FeePaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]