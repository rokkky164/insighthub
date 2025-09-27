from rest_framework.permissions import BasePermission

from accounts.models import User


class IsBusinessUser(BasePermission):
    """
    Allow access only if user is linked to the business (for UserBusinessViewSet).
    """

    def has_object_permission(self, request, view, obj):
        # obj is UserBusiness instance
        return obj.user == request.user or request.user.role == User.Role.ADMIN
