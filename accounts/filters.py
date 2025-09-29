from django_filters import FilterSet, CharFilter
from .models import User


class UserFilter(FilterSet):
    role = CharFilter(field_name="role", lookup_expr="iexact")
    username = CharFilter(field_name="username", lookup_expr="icontains")
    first_name = CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = CharFilter(field_name="last_name", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["role", "username", "first_name", "last_name"]
