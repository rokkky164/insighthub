from django.db.models import (
    ForeignKey,
    DateTimeField,
    CASCADE,
    SET_NULL,
    DecimalField,
    PositiveIntegerField
)
from common.models import GenericModel
from accounts.models import Business
from customers.models import Customer
from products.models import Product


class Sale(GenericModel):
    business = ForeignKey(
        Business,
        on_delete=CASCADE,
        related_name="sales"
    )
    customer = ForeignKey(
        Customer,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="sales"
    )
    date = DateTimeField(auto_now_add=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.business.name}"


class SaleItem(GenericModel):
    sale = ForeignKey(
        Sale,
        on_delete=CASCADE,
        related_name="items"
    )
    product = ForeignKey(
        Product,
        on_delete=SET_NULL,
        null=True,
        related_name="sale_items"
    )
    quantity = PositiveIntegerField(default=1)
    price = DecimalField(max_digits=12, decimal_places=2)  # snapshot of product price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
