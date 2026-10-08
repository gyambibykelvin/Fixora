"""
Django settings for Fixora.
"""

import os
from pathlib import Path

import cloudinary

# ENVIRONMENT VARIABLES

# Load .env locally when python-dotenv is installed.
# Render supplies environment variables directly through the dashboard.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# BASE DIRECTORY

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    if os.environ.get("RENDER"):
        raise RuntimeError(
            "SECRET_KEY must be set in the Render environment."
        )

    # Local-development fallback only
    SECRET_KEY = "django-insecure-local-development-only"


# Render automatically provides the RENDER environment variable.
DEBUG = "RENDER" not in os.environ


# Render automatically provides this hostname.
RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)


# Hosts allowed to access Django
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# CSRF protection for the deployed HTTPS site
CSRF_TRUSTED_ORIGINS = []

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    )


# Render terminates HTTPS before forwarding requests to Django.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# CLOUDINARY

CLOUDINARY_CLOUD_NAME = os.environ.get(
    "CLOUDINARY_CLOUD_NAME"
)

CLOUDINARY_API_KEY = os.environ.get(
    "CLOUDINARY_API_KEY"
)

CLOUDINARY_API_SECRET = os.environ.get(
    "CLOUDINARY_API_SECRET"
)


cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
    "SECURE": True,
    "MEDIA_TAG": "media",
}


# APPLICATIONS

INSTALLED_APPS = [
    "cloudinary",
    "cloudinary_storage",

    "account",
    "core",
    "booking",
    "provider",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# MIDDLEWARE

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise serves Django static files in production.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# URL / TEMPLATE CONFIGURATION

ROOT_URLCONF = "fixora.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "fixora.wsgi.application"


# DATABASE
# SQLite for now, as requested.
#
# IMPORTANT:
# Render's default filesystem is ephemeral. Therefore SQLite data can be lost
# when the service redeploys, restarts, or spins down.
#
# We are intentionally keeping SQLite for this deployment stage.
#

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# FILE STORAGE

# MEDIA:
# User-uploaded files such as:
# - provider profile pictures
# - service images
# - ID documents
#
# go to Cloudinary.
#
# STATIC:
# CSS, JavaScript and static images go through WhiteNoise.
#

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
        ),
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


MEDIA_URL = "/media/"


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"



# PASSWORD VALIDATION


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]



# INTERNATIONALIZATION


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True



# CUSTOM USER MODEL


AUTH_USER_MODEL = "account.User"



# SESSION SETTINGS


SESSION_COOKIE_AGE = 300

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_URL = "/account/login/"



# DEFAULT PRIMARY KEY
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"