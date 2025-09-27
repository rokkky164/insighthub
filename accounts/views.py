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
