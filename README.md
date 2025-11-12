# API для YaMDb
## **REST API** для платформы YaMDb 
**YaMDb** предназначена для сбора отзывов пользователей на произведения различных категорий и жанров.

Аутентифицированные пользователи могут оставлять отзывы к произведениям, комментарии к отзывам других пользователей, а также ставить произведению оценку в диапазоне от 1 до 10.

Из пользовательских оценок формируется средняя оценка произведения — рейтинг.

---

## Технологический стек:

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite

---

## Запуск проекта

Клонировать репозиторий и перейти в него в командной строке.

```
git clone https://github.com/Warmbank/api-for-yamdb
```

```
cd api-for-yamdb/
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```
для Linux/macOS:
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

---

## Документация API

После запуска проекта документация API станет доступна по адресу: http://127.0.0.1:8000/redoc/.

В документации:
- описаны допустимые запросы и структуры ответов на них,
- указаны уровни доступа для выполнения соответствущих запросов,
- описан алгоритм самостоятельной регистрации пользователей,
- указаны возможные роли пользователей с описанием их полномочий.

### Основные эндпойнты и примеры запросов:
Регистрация и аутентификация пользователей: `/api/v1/auth/signup/`, `/api/v1/auth/token/`.

*Пример запроса для регистрации пользователя:*
```
POST /api/v1/auth/signup/
```
```
{
  "email": "email@example.com",
  "username": "username"
}
```

Работа с пользователями, изменение данных пользователя: `/api/v1/users/`, `/api/v1/users/me/`.

*Пример запроса для создания пользователя администратором:*
```
POST /api/v1/users/
```
```
{
    "username": "username",
    "email": "email@example.com",
    "first_name": "Name",
    "last_name": "Surname",
    "bio": "There should be a good story",
    "role": "user"
}
```

Работа с произведениями, категориями и жанрами: `/api/v1/titles/`, `/api/v1/categories/`, `/api/v1/genres/`.

*Пример запроса для создания произведения администратором:*
```
POST /api/v1/titles/
```
```
{
    "name": "title_name",
    "year": 1975,
    "description": "title_description",
    "genre": ["title_genre"],
    "category": "title_category"
}
```

Работа с отзывами и комментариями к ним: `/api/v1/titles/{title_id}/reviews/`, `/api/v1/titles/{title_id}/reviews/{review_id}/comments/`.

*Пример запроса для публикации отзыва на произведение аутентифицированным пользователем:*
```
POST /api/v1/titles/{title_id}/reviews/
```
```
{
    "text": "review_text",
    "score": 10
}
```

## Разработано командой YaMDB:
**Караульный Иван** (https://github.com/Warmbank) - произведения, категории, жанры, рейтинги, отзывы и комментарии.

**Студенников Артем** (https://github.com/ArtemStudenn) - система управления пользователями.
