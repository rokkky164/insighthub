import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Product, ProductCategory


@admin.action(description="Mark selected products as active")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected products as inactive")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Export selected products to CSV")
def export_to_csv(modeladmin, request, queryset):
    field_names = [
        "id",
        "name",
        "sku",
        "category",
        "business",
        "price",
        "stock",
        "low_stock_alert",
        "is_active",
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=products.csv"

    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "business")
    search_fields = ("name", "description")
    list_filter = ("business",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "business",
        "category",
        "price",
        "stock",
        "low_stock_alert",
        "is_active",
    )
    search_fields = ("name", "sku", "description")
    list_filter = ("category", "business", "is_active")
    list_editable = ("stock", "low_stock_alert", "is_active")
    ordering = ("name",)
    actions = [make_active, make_inactive, export_to_csv]
