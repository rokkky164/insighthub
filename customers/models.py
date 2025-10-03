from django.db.models import (
    ForeignKey,
    CharField,
    DateTimeField,
    DateField,
    CASCADE,
    EmailField,
    TextField,
    TextChoices,
    BooleanField,
    DecimalField,
)
from common.models import GenericModel
from business.models import Business


class Party(GenericModel):
    business = ForeignKey(Business, on_delete=CASCADE, related_name="parties")

    # Core identity
    name = CharField(max_length=255)
    email = EmailField(blank=True, null=True)
    phone = CharField(max_length=20, blank=True, null=True)
    secondary_phone = CharField(max_length=20, blank=True, null=True)

    # Demographics
    date_of_birth = DateField(blank=True, null=True)
    gender = CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
    )

    # Contact / location
    address = TextField(blank=True, null=True)
    city = CharField(max_length=100, blank=True, null=True)
    state = CharField(max_length=100, blank=True, null=True)
    country = CharField(max_length=100, blank=True, null=True)
    postal_code = CharField(max_length=20, blank=True, null=True)

    # Engagement / optional
    is_active = BooleanField(default=True)
    loyalty_points = CharField(max_length=20, blank=True, null=True)
    joined_on = DateTimeField(auto_now_add=True)
    last_purchase_on = DateTimeField(blank=True, null=True)

    # Roles
    is_customer = BooleanField(default=False)
    is_supplier = BooleanField(default=False)

    def __str__(self):
        roles = []
        if self.is_customer:
            roles.append("Customer")
        if self.is_supplier:
            roles.append("Supplier")
        return f"{self.name} ({', '.join(roles)})"


class Customer(Party):
    class Meta:
        proxy = True  # no extra table, just filtered view

    def save(self, *args, **kwargs):
        self.is_customer = True
        super().save(*args, **kwargs)


class Supplier(Party):
    account_balance = DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_supplier = True
        super().save(*args, **kwargs)


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
