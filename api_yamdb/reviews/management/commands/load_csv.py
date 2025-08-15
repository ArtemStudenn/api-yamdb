import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review, Comment


class Command(BaseCommand):
    """Команда згрузки CSV."""

    def handle(self, *args, **kwargs):
        data_dir = Path(settings.BASE_DIR) / 'static' / 'data'
        user = get_user_model()

        def load(model, filename, rename=None, batch_size=1000):
            path = data_dir / filename
            if not path.exists():
                return

            objs = []
            with path.open(encoding='utf-8', newline='') as file:
                for row in csv.DictReader(file):
                    if rename:
                        for src, dst in rename.items():
                            if src in row:
                                row[dst] = row.pop(src)
                    objs.append(model(**row))

                    if len(objs) >= batch_size:
                        model.objects.bulk_create(
                            objs,
                            ignore_conflicts=True,
                            batch_size=batch_size
                        )
                        objs.clear()

            if objs:
                model.objects.bulk_create(
                    objs,
                    ignore_conflicts=True,
                    batch_size=batch_size
                )

        load(user, 'users.csv')
        load(Category, 'category.csv')
        load(Genre, 'genre.csv')
        load(Title, 'titles.csv', rename={'category': 'category_id'})
        load(Title.genre.through, 'genre_title.csv')
        load(Review, 'review.csv', rename={'author': 'author_id'})
        load(Comment, 'comments.csv', rename={'author': 'author_id'})

        self.stdout.write(self.style.SUCCESS('CSV загружены'))
