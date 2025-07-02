# academic_journal/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4v#1!8z@k^w$2r7p!b6g3q9x0s%u+zj&l1d4c7v2b5n8m0a3s6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ... (Diğer ayarlar)

# Yeni oluşturduğumuz uygulamaları Django'ya tanıtıyoruz
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bizim uygulamalarımız
    'users',
    'articles',
    'pages',
    'core',
    'dashboard',

    # 3. parti paketler
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'academic_journal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Projenin ana klasöründeki templates dizinini tanıtıyoruz
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Navbar ikonları için kendi context processor'ımızı ekleyeceğiz
                'core.context_processors.notification_context',
            ],
        },
    },
]

# ...

# Veritabanı ayarları
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ...

# Dil ve Zaman ayarları
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Statik ve Medya dosyaları ayarları
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Varsayılan ayarlar
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django'nun varsayılan User modeli yerine kendi modelimizi kullanacağımızı belirtiyoruz
AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = 'anasayfa'