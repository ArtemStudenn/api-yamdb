from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_FIRSTNAME_LENGTH,
    MAX_LASTNAME_LENGTH,
    MAX_CONFIRMATION_CODE_LENGTH,
)
from .validators import username_validator


class RolesChoices(models.TextChoices):
    """Возможные роли для пользователей."""

    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Админ'


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        unique=True,
        max_length=MAX_USERNAME_LENGTH,
        verbose_name='Имя пользователя',
        help_text=(
            'Введите имя пользователя. '
            'Только буквы, цифры и символы @/./+/-/_'
        ),
        validators=(username_validator,)
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту'
    )
    first_name = models.CharField(
        blank=True,
        max_length=MAX_FIRSTNAME_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=MAX_LASTNAME_LENGTH,
        verbose_name='Фамилия',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе',
        help_text='Укажите информацию о себе'
    )
    role = models.CharField(
        choices=RolesChoices.choices,
        default=RolesChoices.USER,
        max_length=max(len(value) for value, _ in RolesChoices.choices),
        verbose_name='Роль пользователя'
    )
    confirmation_code = models.CharField(
        blank=True,
        max_length=MAX_CONFIRMATION_CODE_LENGTH,
        verbose_name='Код подтверждения',
        help_text='Введите код подтверждения'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == RolesChoices.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == RolesChoices.MODERATOR

    def __str__(self):
        return self.username
