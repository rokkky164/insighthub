from django.contrib import admin
from .models import Product, ProductCategory


@admin.action(description="Mark selected products as active")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected products as inactive")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'business')
    search_fields = ('name', 'description')
    list_filter = ('business',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'business', 'category', 'price', 'stock', 'low_stock_alert', 'is_active')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('category', 'business', 'is_active')
    list_editable = ('stock', 'low_stock_alert', 'is_active')
    ordering = ('name',)
    actions = [make_active, make_inactive]
