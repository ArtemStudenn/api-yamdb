from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UsersMeSerializer(UserSerializer):
    """Сериализатор для эндпойта users/me"""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя"""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        required=True,
        max_length=50,
        error_messages={
            'invalid':
            'В имени пользователя допустимы буквы, цифры и символы @/./+/-/_'
        }
    )
    email = serializers.EmailField(
        required=True,
        max_length=150
    )

    def validate(self, data):
        username = data['username']
        email = data['email']
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Данное имя пользователя недоступно'
            )
        if User.objects.filter(username=username).exclude(
            email=email
        ).exists():
            raise serializers.ValidationError(
                'Данное имя пользователя уже используется'
            )
        if User.objects.filter(email=email).exclude(
            username=username
        ).exists():
            raise serializers.ValidationError(
                'Данная электронная почта уже используется'
            )
        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            recipient_list=(user.email,),
            from_email=None,
            fail_silently=False
        )
        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user,
            data['confirmation_code']
        ):
            raise serializers.ValidationError('Неверный код подтверждения')
        return data

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data['username'])
        return {'token': str(AccessToken.for_user(user))}


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
        required=True,
        allow_null=False,
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True,
    )
    year = serializers.IntegerField(required=True)

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

    year = serializers.IntegerField()
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
