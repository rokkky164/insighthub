from rest_framework import viewsets
from .models import User, Business, UserBusiness
from .serializers import UserSerializer, BusinessSerializer, UserBusinessSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Business.objects.prefetch_related(
        'users__user'
    ).all()
    serializer_class = BusinessSerializer



class UserBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserBusiness.objects.select_related('user', 'business').all()
    serializer_class = UserBusinessSerializer
