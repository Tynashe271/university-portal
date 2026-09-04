from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassroomViewSet, DepartmentViewSet, SubjectViewSet, TermViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'terms', TermViewSet)
router.register(r'classrooms', ClassroomViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
