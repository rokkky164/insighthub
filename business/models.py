from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    CASCADE,
    SET_NULL,
    BooleanField
)
from accounts.models import Business, User

from common.models import GenericModel


class Department(GenericModel):
    """
    Departments within a business (e.g., Sales, Marketing, IT).
    """
    business = ForeignKey(
        Business,
        on_delete=CASCADE,
        related_name="departments"
    )
    name = CharField(max_length=100)
    head = ForeignKey(
        User,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments"
    )

    def __str__(self):
        return f"{self.name} - {self.business.name}"


class BusinessSettings(GenericModel):
    """
    Configurable settings for each business.
    (currency, timezone, analytics preferences, etc.)
    """
    business = OneToOneField(
        Business,
        on_delete=CASCADE,
        related_name="settings"
    )
    currency = CharField(max_length=10, default="USD")
    timezone = CharField(max_length=50, default="UTC")
    language = CharField(max_length=20, default="en")
    enable_notifications = BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.business.name}"


class BusinessPlanHistory(GenericModel):
    """
    Tracks subscription plan changes (Free, Pro, Premium).
    """
    business = ForeignKey(
        Business,
        on_delete=CASCADE,
        related_name="plan_history"
    )
    plan_name = CharField(max_length=50)
    start_date = DateField()
    end_date = DateField(null=True, blank=True)  # null = active plan
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.business.name} - {self.plan_name}"
