# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, BusinessSettingsViewSet, PaymentMethodViewSet, BusinessViewSet, UserBusinessViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"settings", BusinessSettingsViewSet, basename="businesssettings")
router.register(r"payment-methods", PaymentMethodViewSet, basename="paymentmethod")
router.register(r"businesses", BusinessViewSet, basename="business")
router.register(r"user-businesses", UserBusinessViewSet, basename="userbusiness")

urlpatterns = [
    path("", include(router.urls)),
]
