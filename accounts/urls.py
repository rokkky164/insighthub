from rest_framework.routers import DefaultRouter
from django.urls import path, re_path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserViewSet, SignupViewSet, LoginView


router = DefaultRouter()

router.register(r"signup", SignupViewSet, basename="signup")
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(
        r"^api/users/login",
        LoginView.as_view(),
        name="user_login",
    ),
]
