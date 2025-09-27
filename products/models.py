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
    DateTimeField
)
from django.db.models import Manager
from django.conf import settings

from common.models import GenericModel
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


class ActiveProductManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


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
    image = URLField(null=True, blank=True)
    objects = ActiveProductManager()
    all_objects = Manager()
    
    class Meta:
        unique_together = ('business', 'sku')
        indexes = [Index(fields=['sku'])]

    def __str__(self):
        return f"{self.name} - {self.sku}"
    
    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class Notification(GenericModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='notifications')
    message = TextField()
    created_at = DateTimeField(auto_now_add=True)
    read = BooleanField(default=False)
