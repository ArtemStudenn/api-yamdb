from django.core.exceptions import ValidationError


def username_validator(username):
    if username.lower() == 'me':
        raise ValidationError('Данное имя пользователя недоступно')
