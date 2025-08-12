from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from .models import User


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
        max_length=50
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
        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError(
                'Данное имя пользователя уже используется'
            )
        if User.objects.filter(email=email).exclude(username=username).exists():
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
