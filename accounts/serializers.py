from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    ChoiceField,
    EmailField,
    CharField,
    ValidationError,
)

from common.utils import generate_username
from .constants import AuthenticateType
from .models import User
from accounts.managers.user_manager import UserManager


class SignupSerializer(ModelSerializer):
    first_name = CharField()
    last_name = CharField()
    password = CharField(write_only=True, validators=[validate_password])
    confirm_password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email",  "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data["username"] = generate_username(validated_data["first_name"], validated_data["last_name"])
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class AuthenticateSerializer(Serializer):

    type = ChoiceField(choices=AuthenticateType.choices())
    email = EmailField(required=False)
    password = CharField(required=False)
    phone = CharField(required=False)
    employee_number = CharField(required=False)
    manager = UserManager()

    def validate(self, attrs):
        auth_type = attrs["type"]
        if auth_type == AuthenticateType.login_with_otp.value:
            return self.validate_for_login_with_otp(attrs)
        if auth_type == AuthenticateType.login_with_password.value:
            return self.manager.validate_and_login_with_email(email=attrs["email"], password=attrs["password"])
    
    # def login_with_password(self, attrs):
    #     user = User.objects.filter(email=attrs["email"]).first()
    #     return self.manager.get_token_for_user(user)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "role"]
