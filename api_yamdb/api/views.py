from django.contrib.auth import get_user_model
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleWriteSerializer,
    TitleReadSerializer,
    UserSerializer,
    UsersMeSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


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


class BaseSlugViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый ViewSet для сущностей со слагом."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(BaseSlugViewSet):
    """Класс представления для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseSlugViewSet):
    """Класс представления для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Класс представления для работы с произведениями."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(rating=Avg('reviews__score'))
            .order_by('id')
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы к произведению."""

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзыву."""

    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)
