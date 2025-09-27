from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

# views.py
from rest_framework import viewsets, permissions
from .models import Department, BusinessSettings, PaymentMethod
from .serializers import DepartmentSerializer, BusinessSettingsSerializer, PaymentMethodSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see departments in their business
        return Department.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)


class BusinessSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only settings of the user's business
        return BusinessSettings.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)
    
    def get(self, request):
        business = request.user.business
        tax_config = getattr(business, 'tax_config', None)
        payment_methods = business.payment_methods.filter(active=True)

        return Response({
            'tax': {
                'name': tax_config.tax_name if tax_config else None,
                'percentage': tax_config.tax_percentage if tax_config else None,
            },
            'currency': {
                'code': business.currency_code,
                'symbol': business.currency_symbol,
            },
            'payment_methods': [pm.method_name for pm in payment_methods],
        })


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)
