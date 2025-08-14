from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


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

    def validate_year(self, value):
        if value is not None and value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один жанр.'
            )
        return value


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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )

    def validate(self, attrs):
        request = self.context['request']
        view = self.context['view']
        if request.method == 'POST':
            title_id = view.kwargs.get('title_id')
            if Review.objects.filter(
                title_id=title_id,
                author=request.user
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв к этому произведению.'
                )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
