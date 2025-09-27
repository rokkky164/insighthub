import django_filters.rest_framework
from rest_framework import viewsets
from .models import User, Business, UserBusiness
from .serializers import UserSerializer, BusinessSerializer, UserBusinessSerializer


class UserFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name="role", lookup_expr='iexact')
    username = django_filters.CharFilter(field_name="username", lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['role', 'username']


class BusinessFilter(django_filters.FilterSet):
    subscription_plan = django_filters.CharFilter(field_name="subscription_plan", lookup_expr='iexact')
    industry = django_filters.CharFilter(field_name="industry", lookup_expr='icontains')

    class Meta:
        model = Business
        fields = ['subscription_plan', 'industry']


class UserBusinessFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name="role", lookup_expr='iexact')
    user__username = django_filters.CharFilter(field_name="user__username", lookup_expr='icontains')
    business__name = django_filters.CharFilter(field_name="business__name", lookup_expr='icontains')

    class Meta:
        model = UserBusiness
        fields = ['role', 'user__username', 'business__name']
