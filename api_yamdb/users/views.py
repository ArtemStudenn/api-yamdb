from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdmin
from .models import User
from .serializers import (
    GetTokenSerializer,
    SignUpSerializer,
    UserSerializer,
    UsersMeSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для модели пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        serializer = UsersMeSerializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_me(self, request):
        serializer = UsersMeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GetTokenView(generics.CreateAPIView):
    """View для получения токена"""

    serializer_class = GetTokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)


class SignUpView(generics.CreateAPIView):
    """View для регистрации пользователя"""

    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
