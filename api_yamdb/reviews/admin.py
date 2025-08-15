from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import Category, Genre, Title, Review, Comment


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'genres_list')
    list_filter = (
        'year',
        'category',
        ('genre', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name',)
    autocomplete_fields = ('category', 'genre')

    @admin.display(description='Жанры')
    def genres_list(self, obj: Title) -> str:
        return ', '.join(g.name for g in obj.genre.all())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('title__name', 'author__username', 'text')
    autocomplete_fields = ('title', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('author__username', 'text')
    autocomplete_fields = ('review', 'author')
