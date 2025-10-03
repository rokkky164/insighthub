from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status, viewsets
from rest_framework.response import Response

# App Imports
from common.exception import InsightHubException
from common.pagination import StandardResultsSetPagination
from common.errors import ERROR_DETAILS
from accounts.models import User
from .serializers import UserSerializer, AuthenticateSerializer, SignupSerializer
from .filters import UserFilter
from .constants import (
    AuthenticateType,
)


class SignupViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully.",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticateAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AuthenticateSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as err:
            if type(err) is ValueError:
                raise InsightHubException(
                    code=err.args[0],
                    detail=ERROR_DETAILS[err.args[0]],
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise err

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginView(AuthenticateAPIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        if "password" in request.data:
            request.data["type"] = AuthenticateType.login_with_password.value
        if "otp" in request.data:
            request.data["type"] = AuthenticateType.login_with_otp.value
        return super().post(request, format)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
