from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    BooleanField,
    CASCADE,
    PositiveIntegerField,
)
from django.utils import timezone

from django.conf import settings
from common.models import GenericModel
from sales.models import Sale, SaleItem, Purchase


class Invoice(GenericModel):
    business = ForeignKey(
        "business.Business", on_delete=CASCADE, related_name="invoices"
    )
    sale = ForeignKey(
        Sale, on_delete=CASCADE, null=True, blank=True, related_name="invoices"
    )
    purchase = ForeignKey(
        Purchase, on_delete=CASCADE, null=True, blank=True, related_name="invoices"
    )
    invoice_number = CharField(max_length=50, unique=True)
    issue_date = DateField(auto_now_add=True)
    due_date = DateField(null=True, blank=True)
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = DecimalField(max_digits=12, decimal_places=2, default=0)
    status = CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
        ],
        default="draft",
    )
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.tax_amount = sum(item.tax_amount for item in self.items.all())
        self.save()


class InvoiceItem(GenericModel):
    invoice = ForeignKey(Invoice, on_delete=CASCADE, related_name="items")
    product = ForeignKey("products.Product", on_delete=CASCADE, null=True, blank=True)
    quantity = PositiveIntegerField(default=1)
    price = DecimalField(max_digits=12, decimal_places=2)
    tax_rate = DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        super().save(*args, **kwargs)
        # update invoice totals automatically
        self.invoice.calculate_total()

    def __str__(self):
        return f"{self.product.name if self.product else 'N/A'} x {self.quantity}"


class BillingPayment(GenericModel):
    invoice = ForeignKey(Invoice, on_delete=CASCADE, related_name="payments")
    amount = DecimalField(max_digits=12, decimal_places=2)
    payment_date = DateTimeField(auto_now_add=True)
    payment_method = CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("card", "Card"), ("online", "Online Payment")],
    )
    is_confirmed = BooleanField(default=True)

    def __str__(self):
        return f"Payment {self.amount} for Invoice {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice status
        total_paid = sum(
            p.amount for p in self.invoice.payments.filter(is_confirmed=True)
        )
        if total_paid >= self.invoice.total_amount:
            self.invoice.status = "paid"
        elif total_paid > 0:
            self.invoice.status = "pending"
        else:
            self.invoice.status = "draft"
        self.invoice.save()


def create_invoice_from_sale(sale: "Sale") -> Invoice:
    """
    Creates an Invoice from a Sale and all its SaleItems.
    Returns the created Invoice instance.
    """
    if not sale or not sale.id:
        raise ValueError("Sale must be saved before creating an invoice.")

    # Generate a unique invoice number (example: INV-YYYYMMDD-ID)
    invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{sale.id}"

    # Create the Invoice linked to the Sale
    invoice = Invoice.objects.create(
        business=sale.customer.business if sale.customer else None,
        sale=sale,
        invoice_number=invoice_number,
        issue_date=timezone.now().date(),
        due_date=None,  # Optional: could be sale_date + 30 days
        status="pending",
    )

    # Create InvoiceItems from SaleItems
    for item in sale.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product=item.product,
            quantity=item.quantity,
            price=item.price,
            tax_rate=getattr(
                item.product, "tax_rate", 0
            ),  # Use product's tax rate if defined
        )

    # Invoice totals are auto-calculated in InvoiceItem.save()
    return invoice


def create_invoice_from_purchase(purchase: "Purchase") -> Invoice:
    """
    Creates an Invoice for a Purchase (supplier invoice) from all its PurchaseItems.
    Returns the created Invoice instance.
    """
    if not purchase or not purchase.id:
        raise ValueError("Purchase must be saved before creating an invoice.")

    # Generate a unique invoice number (example: PINV-YYYYMMDD-ID)
    invoice_number = f"PINV-{timezone.now().strftime('%Y%m%d')}-{purchase.id}"

    # Create the Invoice linked to the Purchase
    invoice = Invoice.objects.create(
        business=purchase.business if hasattr(purchase, "business") else None,
        purchase=purchase,
        invoice_number=invoice_number,
        issue_date=timezone.now().date(),
        due_date=None,  # Optional: could set payment terms
        status="pending",
    )

    # Create InvoiceItems from PurchaseItems
    for item in purchase.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product=item.product,
            quantity=item.quantity,
            price=item.cost_price,
            tax_rate=getattr(item.product, "tax_rate", 0),  # Optional: GST/VAT
        )

    # Invoice totals are auto-calculated in InvoiceItem.save()
    return invoice
