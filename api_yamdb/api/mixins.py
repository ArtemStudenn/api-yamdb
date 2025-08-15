from users.validators import username_validator


class ValidateUsernameMixin:
    """Проверяет валидность имени пользователя."""

    def validate_username(self, username):
        return username_validator(username)
