from pathlib import Path

from decouple import config, Csv
from fabric_expo_management_system.ckeditor_conf import *


PROJECT_NAME = config("PROJECT_NAME")
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")


DEBUG = config('DEBUG', default=False, cast=bool)


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
SITE_BASE_URL = 'http://127.0.0.1:8000'


# Application definition
INSTALLED_APPS = [
    # local apps
    'business_data.apps.BusinessDataConfig',
    'bulk_email.apps.BulkEmailConfig',
    'bulk_wechat.apps.BulkWechatConfig',
    'bulk_whatsapp.apps.BulkWhatsappConfig',
    'bulk_core.apps.BulkCoreConfig',
    'admin_dashboard.apps.AdminDashboardConfig',
    'accounts.apps.AccountsConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "phonenumber_field",
    'django_twilio',
    'django_ckeditor_5',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware', # whitenoise middleware 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fabric_expo_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fabric_expo_management_system.context_processors.sidebar_items', # aside items 
                'fabric_expo_management_system.context_processors.system_info', # system info 
            ],
        },
    },
]

WSGI_APPLICATION = 'fabric_expo_management_system.wsgi.application'


# Database
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASS"),
        "HOST": config("DB_HOST"),
        # "HOST": config("DATABASE_URL"),
        "PORT": "3306",
    }
}


# Database
# DATABASES = {
#     'default': dj_database_url.parse(config('DATABASE_URL'))
# }


# Password validation
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = STATIC_ROOT = BASE_DIR / "staticfiles"


# media directory
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# production storage 
STORAGES = {
    # ...
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'location': MEDIA_ROOT,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = 'admin_dashboard:welcome'
LOGOUT_REDIRECT_URL = 'admin_dashboard:welcome'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL")
EMAIL_HOST_PASSWORD = config("EMAIL_PASS")
EMAIL_FILE_PATH = "/tmp/app-messages"  # change this to a proper location


# django.contrib.auth.tokens.PasswordResetTokenGenerator

# password reset link will expire in 5 mins
PASSWORD_RESET_TIMEOUT = 300


# twilio credentials
TWILIO_ACCOUNT_SID=config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"


# Celery Configuration Options
CELERY_TIMEZONE = "Asia/Dhaka"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = "redis://localhost:6379"
# CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_RESULT_BACKEND = 'django-db'
