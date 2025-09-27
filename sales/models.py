from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE,
    SET_NULL,
    DecimalField,
    IntegerField
)
from common.models import GenericModel
from accounts.models import Business
from customers.models import Customer
from products.models import Product


class Sale(GenericModel):
    business = ForeignKey(Business, on_delete=CASCADE, related_name="sales")
    customer = ForeignKey(Customer, on_delete=SET_NULL, null=True, blank=True, related_name="sales")
    sale_date = DateTimeField(auto_now_add=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2)
    payment_method = CharField(max_length=50, choices=[
        ("cash", "Cash"),
        ("card", "Card"),
        ("online", "Online Payment")
    ])

    def __str__(self):
        return f"Sale #{self.id} - {self.business.name} - {self.total_amount}"


class SaleItem(GenericModel):
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name="items")
    product = ForeignKey(Product, on_delete=SET_NULL, null=True, blank=True, related_name="sale_items")
    quantity = IntegerField(default=1)
    price = DecimalField(max_digits=12, decimal_places=2)  # unit price at the time of sale
    subtotal = DecimalField(max_digits=12, decimal_places=2)  # quantity * price

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
