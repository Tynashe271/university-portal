from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionBankViewSet, AssessmentViewSet, MarkViewSet

router = DefaultRouter()
router.register(r'questions', QuestionBankViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'marks', MarkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]