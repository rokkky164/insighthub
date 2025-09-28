from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE,
    SET_NULL,
    BooleanField,
    DecimalField,
)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from accounts.models import User
from business.constants import BUSINESS_LIST_CACHE_KEY
from common.models import GenericModel


class Business(GenericModel):
    """
    Each tenant (small business) in the SaaS platform.
    """

    name = CharField(max_length=255)
    industry = CharField(max_length=100, blank=True, null=True)
    subscription_plan = CharField(max_length=50, default="Free")

    def __str__(self):
        return self.name


class UserBusiness(GenericModel):
    """
    Link between users and businesses.
    Allows per-business role assignment.
    """

    user = ForeignKey(User, on_delete=CASCADE, related_name="business_roles")
    business = ForeignKey(Business, on_delete=CASCADE, related_name="users")
    role = CharField(max_length=20, choices=User.Role.choices)

    class Meta:
        unique_together = ("user", "business")

    def __str__(self):
        return f"{self.user.username} - {self.business.name} ({self.role})"


class Department(GenericModel):
    """
    Departments within a business (e.g., Sales, Marketing, IT).
    """

    business = ForeignKey(Business, on_delete=CASCADE, related_name="departments")
    name = CharField(max_length=100)
    head = ForeignKey(
        User,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )

    def __str__(self):
        return f"{self.name} - {self.business.name}"


class BusinessSettings(GenericModel):
    business = OneToOneField(Business, on_delete=CASCADE, related_name="settings")
    currency = CharField(max_length=10, default="USD")
    timezone = CharField(max_length=50, default="UTC")
    language = CharField(max_length=20, default="en")
    enable_notifications = BooleanField(default=True)

    # Add tax config fields here or link to a TaxConfig model
    tax_name = CharField(max_length=100, default="GST")
    tax_percentage = DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Settings for {self.business.name}"


class BusinessPlanHistory(GenericModel):
    """
    Tracks subscription plan changes (Free, Pro, Premium).
    """

    business = ForeignKey(Business, on_delete=CASCADE, related_name="plan_history")
    plan_name = CharField(max_length=50)
    start_date = DateField()
    end_date = DateField(null=True, blank=True)  # null = active plan
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.business.name} - {self.plan_name}"


class PaymentMethod(GenericModel):
    business = ForeignKey(Business, on_delete=CASCADE, related_name="payment_methods")
    method_name = CharField(max_length=50)
    active = BooleanField(default=True)

    def __str__(self):
        return f"{self.method_name} ({'Active' if self.active else 'Inactive'})"


@receiver([post_save, post_delete], sender=Business)
def clear_business_cache(sender, **kwargs):
    cache.delete(BUSINESS_LIST_CACHE_KEY)
