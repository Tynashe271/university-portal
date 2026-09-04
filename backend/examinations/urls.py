from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionBankViewSet

router = DefaultRouter()
router.register(r'questions', QuestionBankViewSet)

urlpatterns = [
    path('', include(router.urls)),
]