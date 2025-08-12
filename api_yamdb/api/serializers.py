from rest_framework import serializers
from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Возвращает поля модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Возвращает поля модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Создаёт и изменяет объекты модели Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre'
        )


class TitleReadCategorySerializer(serializers.ModelSerializer):
    """Вложенный сериализатор категории для Title."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadGenreSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор жанра для Title."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Возвращает все поля произведения с вложенными категориями и жанрами."""

    category = TitleReadCategorySerializer()
    genre = TitleReadGenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating'
        )

    def get_rating(self, obj):
        val = getattr(obj, 'rating', None)
        return int(val) if val is not None else None
