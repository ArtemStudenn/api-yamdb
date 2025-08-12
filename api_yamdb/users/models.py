from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Админ'),
)


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя',
        validators=(RegexValidator(regex=r'^[\w.@+-]+$'),)
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту'
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Фамилия',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе',
        help_text='Укажите информацию о себе'
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=15,
        verbose_name='Роль пользователя'
    )
    confirmation_code = models.CharField(
        blank=True,
        max_length=50,
        verbose_name='Код подтверждения',
        help_text='Введите код подтверждения'
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователь'
