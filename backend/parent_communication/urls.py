from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ConferenceScheduleViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'conferences', ConferenceScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]