from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ConferenceScheduleViewSet, ParentProfileViewSet, StudentParentRelationViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'conferences', ConferenceScheduleViewSet)
router.register(r'parents', ParentProfileViewSet)
router.register(r'relations', StudentParentRelationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]