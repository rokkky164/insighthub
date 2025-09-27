from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['category', 'business', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['price', 'stock', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: set is_active = False"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Reactivate a soft-deleted product"""
        product = self.get_object()
        product.is_active = True
        product.save()
        return Response({'status': 'Product activated'})

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """List products that are low on stock"""
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock__lte=models.F('low_stock_alert')
        )
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
