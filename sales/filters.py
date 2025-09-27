import django_filters
from .models import Sale


class SaleFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="sale_date", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="sale_date", lookup_expr='lte')
    customer_id = django_filters.NumberFilter(field_name='customer__id')
    business_id = django_filters.NumberFilter(field_name='business__id')

    class Meta:
        model = Sale
        fields = ['start_date', 'end_date', 'customer_id', 'business_id']
