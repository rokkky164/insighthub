from django.contrib.auth.models import AbstractUser
from django.db.models import (
    TextChoices,
    CharField
)


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
