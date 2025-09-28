import random

from datetime import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from .base_manager import BaseModelManager


class UserManager(BaseModelManager):

    model = User

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.email = kwargs.get("email")
        self.phone = kwargs.get("phone")
        self.password = kwargs.get("password")
        self.otp = kwargs.get("otp")
        self.serializer = kwargs.get("serializer")
        self.user_object = kwargs.get("user_object")
        self.user_id = str(self.user_object.id) if self.user_object is not None else None
        self.user_id = (
            self.user_id if self.user_id is not None else kwargs.get("user_id")
        )
        # self.kc = KeyCloak.init()
        self.username = self.username if self.username else self.email

    @classmethod
    def validate_and_login_with_email(
        cls,
        email,
        password,
        request_meta=None,
    ):
        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            raise ValueError("no_active_user")
        if not user.check_password(password):
            raise ValueError("invalid_credentials")
        jwt = cls.get_token_for_user(user)
        return jwt

    @classmethod
    def get_token_for_user(cls, user):
        refresh = RefreshToken.for_user(user)
        exipry_date = datetime.fromtimestamp(refresh.payload.get("exp"))
        exipry_date = exipry_date + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        data = {
            "token": str(refresh.access_token),
            "expires_in": exipry_date,
            "refresh": str(refresh),
            "user": {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
            },
        }
        return data

    def generate_user_unique_otp():
        while True:
            code = str(random.randint(1000, 9999))
            if not User.objects.filter(otp=code).exists():
                return code

    def generate_user_unique_six_digit_otp():
        while True:
            code = str(random.randint(100000, 999999))
            if not User.objects.filter(otp=code).exists():
                return code

    @classmethod
    def create_verification_code(cls, user):
        code = cls.generate_user_unique_six_digit_otp()
        user.otp = code
        user.otp_created_at = timezone.now()
        user.save()
        return code

    def get_provider_communication_details(id):
        query = User.objects.filter(id=id).first()
        if query is None:
            return None, None, None
        return query.email, query.phone, query.country_code

    def _change_password(self, password):
        self.user_obj.set_password(self.password)
