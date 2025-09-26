from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE
)from common.models import GenericModel
from accounts.models import Business


class ProductCategory(GenericModel):
    business = ForeignKey(
        Business,
        on_delete=CASCADE,
        related_name="product_categories"
    )
    name = CharField(max_length=100)
    description = TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.business.name})"


class Product(GenericModel):
    business = ForeignKey(
        Business,
        on_delete=CASCADE,
        related_name="products"
    )
    category = ForeignKey(
        ProductCategory,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    name = CharField(max_length=255)
    sku = CharField(max_length=50)
    description = TextField(blank=True, null=True)
    price = DecimalField(max_digits=12, decimal_places=2)
    stock = IntegerField(default=0)
    low_stock_alert = IntegerField(default=0)
    is_active = BooleanField(default=True)

    class Meta:
        unique_together = ('business', 'sku')

    def __str__(self):
        return f"{self.name} - {self.sku}"