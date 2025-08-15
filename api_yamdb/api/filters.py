import django_filters as df

from reviews.models import Title


class TitleFilter(df.FilterSet):
    category = df.CharFilter(field_name='category__slug', lookup_expr='exact')
    genre = df.CharFilter(field_name='genre__slug', lookup_expr='exact')
    name = df.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')
