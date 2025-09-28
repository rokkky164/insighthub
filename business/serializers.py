from rest_framework.serializers import ModelSerializer
from accounts.serializers import UserSerializer
from .models import Department, BusinessSettings, PaymentMethod, UserBusiness, Business


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class BusinessSettingsSerializer(ModelSerializer):
    class Meta:
        model = BusinessSettings
        fields = "__all__"


class PaymentMethodSerializer(ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class UserBusinessSimpleSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ["user", "role"]


class BusinessSerializer(ModelSerializer):
    users = UserBusinessSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = ["id", "name", "industry", "subscription_plan", "users"]


class UserBusinessSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ["id", "user", "business", "role", "created_at"]
