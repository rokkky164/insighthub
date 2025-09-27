from django.core.cache import cache

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.pagination import StandardResultsSetPagination
from .models import User, Business, UserBusiness
from .serializers import UserSerializer, BusinessSerializer, UserBusinessSerializer
from .filters import UserFilter, BusinessFilter, UserBusinessFilter
from .permissions import IsBusinessUser
from .constants import BUSINESS_LIST_CACHE_KEY, BUSINESS_LIST_CACHE_TIMEOUT


class AuthenticateAPIView(LoggingMixin, generics.GenericAPIView):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = AuthenticateSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            if type(e) is ValueError:
                raise StandardAPIException(
                    code=e.args[0],
                    detail=ERROR_DETAILS[e.args[0]],
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise e

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginView(AuthenticateAPIView):
    def post(self, request, format=None):
        request.data["type"] = AuthenticateType.login_with_password.value
        return super().post(request, format)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]


class BusinessViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = BusinessFilter

    def list(self, request, *args, **kwargs):
        cache_key = f"{BUSINESS_LIST_CACHE_KEY}_page_{request.query_params.get('page', 1)}"
        cached_data = cache.get(cache_key)

        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, BUSINESS_LIST_CACHE_TIMEOUT)
            return response

        return Response(cached_data)


class UserBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserBusiness.objects.select_related('user', 'business').all()
    serializer_class = UserBusinessSerializer
    filterset_class = UserBusinessFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsBusinessUser]
