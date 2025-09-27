from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserViewSet, BusinessViewSet, UserBusinessViewSet, SignupViewSet


router = DefaultRouter()

router.register(r"signup", SignupViewSet, basename="signup")
router.register(r"users", UserViewSet, basename="user")
router.register(r"businesses", BusinessViewSet, basename="business")
router.register(r"user-businesses", UserBusinessViewSet, basename="userbusiness")

urlpatterns = [
    path("", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
