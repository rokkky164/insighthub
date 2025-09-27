from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, BusinessViewSet, UserBusinessViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'user-businesses', UserBusinessViewSet, basename='userbusiness')

urlpatterns = [
    path('', include(router.urls)),
]
