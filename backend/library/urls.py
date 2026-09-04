from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookCheckoutViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'checkouts', BookCheckoutViewSet)

urlpatterns = [
    path('', include(router.urls)),
]