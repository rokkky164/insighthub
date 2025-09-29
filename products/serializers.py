from rest_framework import serializers
from business.models import Business
from .models import ProductCategory, Product


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "name", "industry", "subscription_plan"]  # match your model


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "description"]  # no nested business here


class ProductSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()  # nested creation
    category = serializers.CharField(required=False, allow_null=True)  # just name

    class Meta:
        model = Product
        fields = [
            "id",
            "business",
            "category",
            "name",
            "sku",
            "description",
            "price",
            "stock",
            "low_stock_alert",
            "is_active",
            "image",
        ]

    def create(self, validated_data):
        # Handle business
        business_data = validated_data.pop("business")
        business, _ = Business.objects.get_or_create(**business_data)

        # Handle category
        category_name = validated_data.pop("category", None)
        category = None
        if category_name:
            category, _ = ProductCategory.objects.get_or_create(
                business=business,
                name=category_name
            )

        # Create product
        product = Product.objects.create(
            business=business,
            category=category,
            **validated_data
        )
        return product
