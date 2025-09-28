from django.contrib.auth.models import AbstractUser
from django.db.models import (
    TextChoices,
    CharField,
    ForeignKey,
    CASCADE,
)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from accounts.constants import BUSINESS_LIST_CACHE_KEY
from accounts.managers.base_manager import BaseModelManager

from common.models import GenericModel


class User(AbstractUser):
    """
    Custom user model with global role (optional).
    Roles: Admin, Manager, Viewer.
    """

    class Role(TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        VIEWER = "VIEWER", "Viewer"

    role = CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)

    def __str__(self):
        return f"{self.username} ({self.role})"


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


@receiver([post_save, post_delete], sender=Business)
def clear_business_cache(sender, **kwargs):
    cache.delete(BUSINESS_LIST_CACHE_KEY)
