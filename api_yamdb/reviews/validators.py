from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_future_year(value: int):
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего.')
