from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdmissionApplicationViewSet, MeritListViewSet

router = DefaultRouter()
router.register(r'applications', AdmissionApplicationViewSet)
router.register(r'merit-lists', MeritListViewSet)

urlpatterns = [
    path('', include(router.urls)),
]