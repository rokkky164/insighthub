from django.db.models import (
    ForeignKey,
    CharField,
    CASCADE,
    Index,
    TextField,
    SET_NULL,
    DecimalField,
    IntegerField,
    BooleanField,
    URLField,
)
from django.db.models import Manager
from django.conf import settings

from common.models import GenericModel
from business.models import Business


class ProductCategory(GenericModel):
    business = ForeignKey(
        Business, on_delete=CASCADE, related_name="product_categories"
    )
    name = CharField(max_length=100)
    description = TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.business.name})"


class ActiveProductManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Product(GenericModel):
    business = ForeignKey(Business, on_delete=CASCADE, related_name="products")
    category = ForeignKey(
        "ProductCategory",
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = CharField(max_length=255)
    sku = CharField(max_length=50)  # Base SKU
    barcode = CharField(max_length=100, blank=True, null=True)
    description = TextField(blank=True, null=True)
    unit_of_measure = CharField(max_length=20, default="unit")  # e.g. kg, liter, pcs
    is_service = BooleanField(default=False)  # For services (skip stock tracking)
    tax_rate = DecimalField(max_digits=5, decimal_places=2, default=0)  # GST/VAT %
    is_active = BooleanField(default=True)
    image = URLField(null=True, blank=True)

    objects = Manager()  # Normal manager

    class Meta:
        unique_together = ("business", "sku")
        indexes = [Index(fields=["sku"])]

    def __str__(self):
        return f"{self.name} - {self.sku}"

    def delete(self, *args, **kwargs):
        # Soft delete
        self.is_active = False
        self.save()


class ProductVariant(GenericModel):
    product = ForeignKey(Product, on_delete=CASCADE, related_name="variants")
    sku = CharField(max_length=50, unique=True)  # Each variant has its own SKU
    name = CharField(max_length=100)  # e.g. "Red - M", "1 Kg Pack"
    price = DecimalField(max_digits=12, decimal_places=2)
    stock = IntegerField(default=0)
    low_stock_alert = IntegerField(default=0)
    barcode = CharField(max_length=100, blank=True, null=True)
    is_active = BooleanField(default=True)

    class Meta:
        indexes = [Index(fields=["sku"])]

    def __str__(self):
        return f"{self.product.name} ({self.name})"


class ProductPrice(GenericModel):
    product = ForeignKey(Product, on_delete=CASCADE, related_name="prices")
    variant = ForeignKey(
        ProductVariant, on_delete=CASCADE, related_name="prices", null=True, blank=True
    )
    price_type = CharField(
        max_length=20,
        choices=[
            ("retail", "Retail"),
            ("wholesale", "Wholesale"),
            ("member", "Member"),
            ("special", "Special"),
        ],
        default="retail",
    )
    amount = DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("product", "variant", "price_type")

    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.name} ({self.price_type})"
        return f"{self.product.name} ({self.price_type})"


class Notification(GenericModel):
    user = ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="notifications"
    )
    message = TextField()
    read = BooleanField(default=False)
