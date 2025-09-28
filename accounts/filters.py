from django_filters import FilterSet, CharFilter
from .models import User


class UserFilter(FilterSet):
    role = CharFilter(field_name="role", lookup_expr="iexact")
    username = CharFilter(field_name="username", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["role", "username"]
