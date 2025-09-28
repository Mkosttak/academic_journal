# academic_journal/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4v#1!8z@k^w$2r7p!b6g3q9x0s%u+zj&l1d4c7v2b5n8m0a3s6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

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
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.monitoring.MonitoringMiddleware',  # Monitoring middleware
    'core.rate_limiting.RateLimitMiddleware',  # Rate limiting middleware
]

# Güvenlik ayarları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF ayarları
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'https://localhost:8000']

# Session güvenliği
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

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
                'core.context_processors.site_settings',
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

# CDN Configuration
USE_CDN = os.environ.get('USE_CDN', 'False').lower() == 'true'

if USE_CDN and not DEBUG:
    # AWS S3 CDN Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-west-1')
    
    # S3 Settings
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=31536000',  # 1 yıl
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_VERIFY = True
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    # CDN Headers
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=31536000',
        'ContentDisposition': 'inline'
    }
    
    # CloudFront CDN (optional)
    AWS_CLOUDFRONT_DOMAIN = os.environ.get('AWS_CLOUDFRONT_DOMAIN')
    if AWS_CLOUDFRONT_DOMAIN:
        STATIC_URL = f'https://{AWS_CLOUDFRONT_DOMAIN}/static/'
        MEDIA_URL = f'https://{AWS_CLOUDFRONT_DOMAIN}/media/'
else:
    # Local development settings
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

# Varsayılan ayarlar
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django'nun varsayılan User modeli yerine kendi modelimizi kullanacağımızı belirtiyoruz
AUTH_USER_MODEL = 'users.User'

LOGIN_REDIRECT_URL = 'anasayfa'

# Cache ayarları
USE_REDIS = os.environ.get('USE_REDIS', 'False').lower() == 'true'

if USE_REDIS:
    # Redis cache (production için)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 300,
            'KEY_PREFIX': 'academic_journal',
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/2',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 86400,  # 24 saat
            'KEY_PREFIX': 'sessions',
        },
        'api': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/3',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 600,  # 10 dakika
            'KEY_PREFIX': 'api',
        }
    }
    # Session cache backend
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'sessions'
else:
    # Memory cache (development için)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }
    # Session backend
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging yapılandırması
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.monitoring': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# E-posta ayarları (backup bildirimleri için)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Admin e-posta ayarları
ADMINS = [
    ('Admin', 'admin@yourdomain.com'),
]

# Backup ayarları
BACKUP_SETTINGS = {
    'BACKUP_DIR': os.path.join(BASE_DIR, 'backups'),
    'DAYS_TO_KEEP': 30,
    'SEND_NOTIFICATIONS': True,
}

# Database optimizasyonu (SQLite için)
DATABASES['default']['OPTIONS'] = {
    'timeout': 20,
}