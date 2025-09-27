from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CharField,
    IntegerField,
    ValidationError,
)
from .models import Sale, SaleItem
from products.models import Product


class SaleItemSerializer(ModelSerializer):
    product_name = CharField(source="product.name", read_only=True)

    class Meta:
        model = SaleItem
        fields = ["id", "product", "product_name", "quantity", "price", "subtotal"]


class SaleSerializer(ModelSerializer):
    items = SaleItemSerializer(many=True)
    customer_name = CharField(source="customer.name", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "business",
            "customer",
            "customer_name",
            "sale_date",
            "payment_method",
            "total_amount",
            "items",
        ]
        read_only_fields = ["total_amount", "sale_date"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        sale = Sale.objects.create(**validated_data)

        total = 0
        for item in items_data:
            product = item["product"]
            price = item.get("price") or product.price
            quantity = item["quantity"]
            subtotal = price * quantity

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price,
                subtotal=subtotal,
            )

            # Deduct inventory
            product.inventory_quantity -= quantity
            product.save()

            total += subtotal

        sale.total_amount = total
        sale.save()
        return sale


class ReturnSerializer(Serializer):
    sale_item_id = IntegerField()
    quantity = IntegerField()
    reason = CharField(allow_blank=True)

    def validate(self, data):
        item = SaleItem.objects.get(id=data["sale_item_id"])
        if data["quantity"] > item.quantity:
            raise ValidationError("Cannot return more than sold quantity.")
        return data

    def create(self, validated_data):
        item = SaleItem.objects.get(id=validated_data["sale_item_id"])
        item.product.inventory_quantity += validated_data["quantity"]
        item.product.save()
        # optional: create Return model entry
        return validated_data
