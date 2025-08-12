from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters

from reviews.models import Category, Genre, Title
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleWriteSerializer,
    TitleReadSerializer,
)
from api.permissions import IsAdminOrReadOnly
from api.filters import TitleFilter


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
        return super().get_queryset().annotate(rating=Avg('reviews__score'))
