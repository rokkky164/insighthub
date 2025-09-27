from rest_framework import serializers
from .models import User, Business, UserBusiness


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class UserBusinessSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ['id', 'user', 'business', 'role', 'created_at']


class UserBusinessSimpleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ['user', 'role']


class BusinessSerializer(serializers.ModelSerializer):
    users = UserBusinessSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'name', 'industry', 'subscription_plan', 'users']
