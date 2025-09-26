from django.db.models import (
    ForeignKey,
    CharField,
    DateField,
    DateTimeField,
    OneToOneField,
    SET_NULL
)
from django.conf import settings


class GenericModel(Model):
    """
    Abstract base model for audit fields.
    Tracks who created/updated a record and when.
    """
    created_by = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )
    created_on = DateTimeField(auto_now_add=True)

    updated_by = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated"
    )
    updated_on = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
