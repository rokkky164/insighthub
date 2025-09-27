from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    ChoiceField,
    EmailField,
    CharField,
    ValidationError
)
from .models import User, Business, UserBusiness


class AuthenticateVersion2Serializer(Serializer):

    type = ChoiceField(choices=AuthenticateType.choices())
    email = EmailField(required=False)
    password = CharField(required=False)
    phone = CharField(required=False)
    employee_number = CharField(required=False)

    manager = VMSUserManager()

    def validate_for_login_with_password(self, attrs):
        if ("email" not in attrs.keys() or "password" not in attrs.keys()) or (
            attrs["email"] is None or attrs["password"] is None
        ):
            raise ValidationError(
                detail=ERROR_DETAILS["req_param_missing_email"],
                code="req_param_missing_email",
            )
        user_data = self.manager.validate_and_login_with_email(
            attrs["email"],
            attrs["password"],
            self.context.get("request").META,
        )
        user_id = user_data["user"]["user_id"]
        user = VMSUser.objects.get(id=user_id)
        user_roles = UserRoleSerializer(
            UserRoleMapping.objects.filter(user=user), many=True
        ).data
        user_data["user"]["user_roles"] = user_roles
        return user_data

    # UPDATED NEW AREA
    @staticmethod
    def login_with_password(attrs):
        user_manager = VMSUserManager(
            username=attrs.get("username"),
            email=attrs.get("email"),
            password=attrs.get("password"),
        )
        return user_manager.validate_and_login_with_email(
            device_detail=attrs.get("device_detail"),
            location_detail=attrs.get("location_detail", {}),
        )

    def validate_for_login_with_otp(self, attrs):
        if "mobile" not in attrs.keys() and "email" not in attrs.keys():
            raise ValidationError(
                detail=ERROR_DETAILS["req_param_missing"], code="req_param_missing"
            )
        return self.manager.send_otp_to_user(
            attrs.get("email", None), attrs.get("mobile", None)
        )

    @staticmethod
    def validate_for_otp(attrs):
        if ("phone" not in attrs.keys() and "email" not in attrs.keys()) or attrs[
            "otp"
        ] is None:
            raise ValidationError(
                detail=ERROR_DETAILS["req_param_missing"], code="req_param_missing"
            )

    @staticmethod
    def login_with_otp(attrs):
        username = attrs.get("email") if attrs.get("email") else attrs.get("phone")
        user_manager = VMSUserManager(
            username=username,
            email=attrs.get("email"),
        )
        return user_manager.validate_otp_and_login(
            mobile=attrs.get("mobile", None),
            email=attrs.get("email", None),
            otp=attrs["otp"],
            device_detail=attrs.get("device_detail", None),
            location_detail=attrs.get("location_detail", {}),
        )

    @staticmethod
    def validate_for_security_question(attrs):
        if (
            ("mobile" not in attrs.keys() and "email" not in attrs.keys())
            or "question_id" not in attrs.keys()
            or "answer" not in attrs.keys()
        ):
            raise ValidationError(
                detail=ERROR_DETAILS["req_param_missing"], code="req_param_missing"
            )

    @staticmethod
    def login_with_security_question(attrs):
        username = attrs.get("email") if attrs.get("email") else attrs.get("mobile")
        user_manager = VMSUserManager(
            username=username,
            email=attrs.get("email"),
        )

        return user_manager.validate_security_answer_and_login(
            attrs["question_id"],
            attrs["answer"],
            attrs["mobile"] if "mobile" in attrs else None,
            attrs["email"] if "email" in attrs else None,
            attrs.get("device_detail", None),
            attrs.get("location_detail", {}),
        )

    def validate(self, attrs):
        auth_type = attrs["type"]
        if auth_type == AuthenticateType.login_with_otp.value:
            return self.validate_for_login_with_otp(attrs)
        if auth_type == AuthenticateType.login_with_password.value:
            self.validate_for_login_with_password(attrs=attrs)
            return self.login_with_password(attrs=attrs)
        if auth_type == AuthenticateType.validate_otp.value:
            self.validate_for_otp(attrs=attrs)
            return self.login_with_otp(attrs=attrs)
        if auth_type == AuthenticateType.validate_security_question.value:
            self.validate_for_security_question(attrs)
            return self.login_with_security_question(attrs=attrs)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class UserBusinessSimpleSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ['user', 'role']


class BusinessSerializer(ModelSerializer):
    users = UserBusinessSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'name', 'industry', 'subscription_plan', 'users']


class UserBusinessSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = UserBusiness
        fields = ['id', 'user', 'business', 'role', 'created_at']

