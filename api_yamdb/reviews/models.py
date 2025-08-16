from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import (
    MIN_SCORE,
    MAX_SCORE,
    MAX_STRING_LEN,
    SLUG_DISPLAY_MAX_LEN,
)
from .validators import validate_not_future_year


class NameSlugAbstract(models.Model):
    """Абстрактная моель для категории и жанра."""

    name = models.CharField(max_length=MAX_STRING_LEN, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.slug[:SLUG_DISPLAY_MAX_LEN]


class AuthorTextPubDateAbstract(models.Model):
    """Абстрактная моель для комментариев и оценки."""

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Category(NameSlugAbstract):
    """Категория произведений."""

    class Meta(NameSlugAbstract.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugAbstract):
    """Жанр произведений."""

    class Meta(NameSlugAbstract.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведение."""

    name = models.CharField(
        max_length=MAX_STRING_LEN,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        validators=[validate_not_future_year],
        db_index=True,
        null=True,
        verbose_name='Год выпуска'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:SLUG_DISPLAY_MAX_LEN]


class Review(AuthorTextPubDateAbstract):
    """Отзыв пользователя на произведение (1..10)."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_SCORE, message=f'Оценка не может быть ниже {MIN_SCORE}.'
            ),
            MaxValueValidator(
                MAX_SCORE, message=f'Оценка не может быть выше {MAX_SCORE}.'
            ),
        ),
        verbose_name='Оценка',
    )

    class Meta(AuthorTextPubDateAbstract.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review_per_title_author',
            ),
        )

    def __str__(self):
        return f'{self.author} — {self.title} — {self.score}'


class Comment(AuthorTextPubDateAbstract):
    """Комментарий к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(AuthorTextPubDateAbstract.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:SLUG_DISPLAY_MAX_LEN]
