import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.environ.get("ENVIRONMENT", "DEVELOPMENT")

# Add src directory to Python path
sys.path.insert(0, str(BASE_DIR / "src"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
CORS_ALLOW_ALL_ORIGINS = True

# Application definition
INSTALLED_APPS = [
    "corsheaders",
    "src.apps.memes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "db"),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "pt-br"
LANGUAGES = [("es", _("Spanish")), ("en", _("English")), ("pt-br", _("Portuguese"))]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

CREDENTIALS_DICT = {
    "type": "service_account",
    "project_id": "wtm-international",
    "private_key_id": os.environ.get("PRIVATE_KEY_BUCKET_ID"),
    "private_key": os.environ.get("PRIVATE_KEY_BUCKET").replace("\\n", "\n").replace('"', ""),
    "client_email": os.environ.get("ACCOUNT_GCP_EMAIL"),
    "client_id": os.environ.get("CLIENT_ID_BUCKET"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.environ.get('ACCOUNT_GCP_NAME')}%40wtm-international.iam.gserviceaccount.com",  # noqa  E501
}
GS_CREDENTIALS = service_account.Credentials.from_service_account_info(CREDENTIALS_DICT)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django,contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if ENVIRONMENT != "DEVELOPMENT":
    STORAGES.update(
        {
            "default": {
                "BACKEND": "config.gcloud.GoogleCloudMediaFileStorage",
                "OPTIONS": {
                    "bucket_name": os.environ.get("BUCKET_NAME"),
                    "project_id": "wtm-international",
                    "credentials": GS_CREDENTIALS,
                },
            },
        }
    )

if ENVIRONMENT == "PRODUCTION":
    if DEBUG:
        print("\033[31m**** CAUTION: You are running in production with DEBUG=True ****\033[0;0m")
    if ALLOWED_HOSTS.__contains__("*"):
        print("\033[31m**** CAUTION: You are running in production with ALLOWED_HOSTS=* ****\033[0;0m")
