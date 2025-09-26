from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SaleItem, Product


@receiver(post_save, sender=SaleItem)
def update_product_stock_on_save(sender, instance, created, **kwargs):
    """
    Decrement product stock when a SaleItem is created.
    If updated, adjust stock accordingly.
    """
    product = instance.product
    if not product:
        return

    if created:
        product.stock -= instance.quantity
    else:
        # When updating, calculate difference
        old_instance = sender.objects.get(pk=instance.pk)
        difference = instance.quantity - old_instance.quantity
        product.stock -= difference

    product.stock = max(product.stock, 0)  # prevent negative stock
    product.save()


@receiver(post_delete, sender=SaleItem)
def restore_product_stock_on_delete(sender, instance, **kwargs):
    """
    Restore product stock if a SaleItem is deleted.
    """
    product = instance.product
    if not product:
        return

    product.stock += instance.quantity
    product.save()
