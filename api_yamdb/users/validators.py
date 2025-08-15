import re

from django.core.exceptions import ValidationError

from .constants import ALLOWED_USERNAME_SYMBOLS


def username_validator(username):
    if username.lower() == 'me':
        raise ValidationError('Данное имя пользователя недоступно')
    not_allowed_symbols = re.sub(ALLOWED_USERNAME_SYMBOLS, '', username)
    if not_allowed_symbols:
        raise ValidationError(
            'Имя пользователя должно содержать только '
            'буквы, цифры и символы @/./+/-/_'
        )
    return username
