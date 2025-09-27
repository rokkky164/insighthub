from  django_filters import FilterSet, CharFilter
from .models import User, Business, UserBusiness


class UserFilter(FilterSet):
    role = CharFilter(field_name="role", lookup_expr='iexact')
    username = CharFilter(field_name="username", lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['role', 'username']


class BusinessFilter(FilterSet):
    subscription_plan = CharFilter(field_name="subscription_plan", lookup_expr='iexact')
    industry = CharFilter(field_name="industry", lookup_expr='icontains')

    class Meta:
        model = Business
        fields = ['subscription_plan', 'industry']


class UserBusinessFilter(FilterSet):
    role = CharFilter(field_name="role", lookup_expr='iexact')
    user__username = CharFilter(field_name="user__username", lookup_expr='icontains')
    business__name = CharFilter(field_name="business__name", lookup_expr='icontains')

    class Meta:
        model = UserBusiness
        fields = ['role', 'user__username', 'business__name']
