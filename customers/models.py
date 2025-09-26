from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE
)
from common.models import GenericModel
from accounts.models import Business


class Customer(GenericModel):
    """
    End customers of a business.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.business.name})"


class CustomerNote(GenericModel):
    """
    Notes about a customer (e.g., preferences, issues, history).
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.customer.name}"


class CustomerInteraction(GenericModel):
    """
    Log of interactions with the customer.
    (calls, emails, meetings, etc.)
    """
    class InteractionType(models.TextChoices):
        CALL = "CALL", "Call"
        EMAIL = "EMAIL", "Email"
        MEETING = "MEETING", "Meeting"
        OTHER = "OTHER", "Other"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="interactions"
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices,
        default=InteractionType.OTHER
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interaction_type} with {self.customer.name}"
