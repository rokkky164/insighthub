# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, BusinessSettingsViewSet, PaymentMethodViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'settings', BusinessSettingsViewSet, basename='businesssettings')
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')

urlpatterns = [
    path('', include(router.urls)),
]
