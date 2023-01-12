import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
# imported permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# third-party
from rest_framework_simplejwt.views import TokenRefreshView

# imported models
from .models import User
# imported serializer
from .serializers import (ChangePasswordSerializer, LoginSerializer, LogoutSerializer,
                          RegisterUserSerializer, UpdateUserSerializer, UserListSerializer)
from .user_permissions import (UserChangePasswordPermissions, UserRegisterPermission, UserRetrievePermission,
                               UserUpdatePermissions, UserViewPermissions)


# IPAddress


#  custom jwt refresh token purchase_order_view
class NewTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)


# user registration purchase_order_view for admin
class UserRegisterView(CreateAPIView):
    permission_classes = [UserRegisterPermission]
    serializer_class = RegisterUserSerializer

    @transaction.atomic
    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Jwt login and token response
class UserLoginView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            # saving user login information to log database
            # save_user_log(request, purchase_order_serializer.data['id'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  refresh token blacklist on logout
class UserLogout(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    @transaction.atomic
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"Logout successful"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# user update for admin and other users
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [UserUpdatePermissions]
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer

    def patch(self, request, pk, **kwargs):
        user_object = self.get_object()
        serializer = UpdateUserSerializer(user_object, data=request.data, partial=True, context={'request': request,
                                                                                                 'pk': pk})  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  change password for common users
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [UserChangePasswordPermissions]
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    http_method_names = ['patch']


class FilterForUsers(django_filters.FilterSet):
    user_name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = User
        fields = ['id', 'user_name', 'groups']


#  users list for admin
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [UserViewPermissions]
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_class = FilterForUsers
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["mobile_no", "user_name", 'email']
    ordering_fields = ['id']

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [UserViewPermissions]
        elif self.action == 'retrieve':
            self.permission_classes = [UserRetrievePermission]
        return super(self.__class__, self).get_permissions()
