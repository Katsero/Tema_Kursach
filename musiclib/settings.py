"""
Django settings for musiclib project.

Специально настроен под курсовой проект:
«Анонимная бесплатная библиотека музыки».

Основные особенности:
- Нет пользовательской регистрации — всё анонимно.
- Поддержка загрузки аудиофайлов.
- REST API через DRF.
- Поддержка русского языка и локали.
- Готов к расширению: Docker, тесты, OpenAPI и др.
"""

from pathlib import Path
import os

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Для разработки допустимо, но в продакшене — только через .env
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-_f@zn@!6u-41fy#dpgtiwntsk#p%^g0sb$d-o5zg631#k_y*s-'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Разрешённые хосты (для разработки — localhost и 127.0.0.1)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Приложения проекта
INSTALLED_APPS = [
    # Встроенные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Сторонние приложения
    'rest_framework',
    'corsheaders',  # для CORS (если фронт на другом порту)
    # Локальные приложения
    'music',  # основное приложение проекта
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # должен быть как можно раньше
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # поддержка i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL-конфигурация
ROOT_URLCONF = 'musiclib.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # для {{ MEDIA_URL }}
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'musiclib.wsgi.application'

# База данных (по умолчанию SQLite — подходит для учебного проекта)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей (не используется, т.к. нет регистрации, но оставлено)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Локализация
LANGUAGE_CODE = 'ru-ru'  # Русский язык по умолчанию
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, JS, изображения)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Медиафайлы (загруженные пользователем аудиофайлы и обложки)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS — разрешаем все источники (только для разработки!)
# В продакшене ограничить до конкретных доменов
CORS_ALLOW_ALL_ORIGINS = True

# DRF настройки
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Тип первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'