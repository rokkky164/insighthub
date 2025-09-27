from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product
from .constants import LOW_STOCK_THRESHOLD
from sales.models import SaleItem


def check_low_stock():
    low_stock_products = Product.objects.filter(
        inventory_quantity__lt=LOW_STOCK_THRESHOLD
    )
    if low_stock_products.exists():
        # Send notification to admin/staff
        for product in low_stock_products:
            notify_low_stock(product)


def notify_low_stock(product):
    # Placeholder: You can send email, push notification, or in-app notification
    message = f"Low stock alert: {product.name} has only {product.inventory_quantity} items left."
    # e.g., send_email_to_admins(message)
    print(message)  # For demo purpose


@receiver(post_save, sender=SaleItem)
def update_inventory_and_check_stock(sender, instance, **kwargs):
    product = instance.product
    if product:
        # Deduct sold quantity from inventory
        product.inventory_quantity -= instance.quantity
        product.save()

        # Check low stock after update
        if product.inventory_quantity < LOW_STOCK_THRESHOLD:
            notify_low_stock(product)
