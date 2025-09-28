from django.db.models import (
    ForeignKey,
    CharField,
    DateTimeField,
    CASCADE,
    EmailField,
    TextField,
    TextChoices,
)
from common.models import GenericModel
from business.models import Business


class Customer(GenericModel):
    """
    End customers of a business.
    """

    business = ForeignKey(Business, on_delete=CASCADE, related_name="customers")
    name = CharField(max_length=255)
    email = EmailField(blank=True, null=True)
    phone = CharField(max_length=20, blank=True, null=True)
    address = TextField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.business.name})"


class CustomerNote(GenericModel):
    """
    Notes about a customer (e.g., preferences, issues, history).
    """

    customer = ForeignKey(Customer, on_delete=CASCADE, related_name="notes")
    note = TextField()
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.customer.name}"


class CustomerInteraction(GenericModel):
    """
    Log of interactions with the customer.
    (calls, emails, meetings, etc.)
    """

    class InteractionType(TextChoices):
        CALL = "CALL", "Call"
        EMAIL = "EMAIL", "Email"
        MEETING = "MEETING", "Meeting"
        OTHER = "OTHER", "Other"

    customer = ForeignKey(Customer, on_delete=CASCADE, related_name="interactions")
    interaction_type = CharField(
        max_length=20, choices=InteractionType.choices, default=InteractionType.OTHER
    )
    description = TextField(blank=True, null=True)
    date = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interaction_type} with {self.customer.name}"
