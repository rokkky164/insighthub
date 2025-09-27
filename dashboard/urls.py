from django.urls import path
from .views import (
    DashboardView, SalesCSVExportView, SalesChartView, ProductSalesChartView, CustomerSalesChartView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/sales/export/', SalesCSVExportView.as_view(), name='sales_export'),
    path('reports/sales/export/', SalesChartView.as_view(), name='sales_chart'),
    path('reports/sales/chart/product-wise/', ProductSalesChartView.as_view(), name='product_sales_chart'),
    path('reports/sales/chart/customer-wise/', CustomerSalesChartView.as_view(), name='customer_sales_chart'),
]

