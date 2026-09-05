from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClubViewSet, ClubMembershipViewSet, ClubEventViewSet, AchievementViewSet

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'memberships', ClubMembershipViewSet)
router.register(r'events', ClubEventViewSet)
router.register(r'achievements', AchievementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
