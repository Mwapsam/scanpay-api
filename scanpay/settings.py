import os
from pathlib import Path
import environ
import dj_database_url
from corsheaders.defaults import default_headers

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


SECRET_KEY = "django-insecure-pt6b@2g5ex)mo%q4_!_+(va-+-jki3tsi9l7_&bftjo8d$3&91"

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #Installed Apps
    "rest_framework",
    "corsheaders",
    "oauth2_provider",
    "anymail",
    #Custom Apps
    "users",
    "sales",
    "ledger",
    "app_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "scanpay.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "scanpay.wsgi.application"


default_database = {
    "ENGINE": os.environ.get("POSTGRES_ENGINE", "django.db.backends.sqlite3"),
    "NAME": os.environ.get(
        "POSTGRES_NAME", os.path.join(BASE_DIR, BASE_DIR / "db.sqlite3")
    ),
    "USER": os.environ.get("POSTGRES_USER", None),
    "PASSWORD": os.environ.get("POSTGRES_PASSWORD", None),
    "HOST": os.environ.get("POSTGRES_HOST", None),
    "PORT": os.environ.get("POSTGRES_PORT", None),
}

postgres_url = os.environ.get(
    "POSTGRES_URL",
    "postgres://default:03mZLFHhWwyq@ep-lucky-cloud-a4fxbtiw-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require",
)

if postgres_url:
    DATABASES = {"default": dj_database_url.parse(postgres_url)}
else:
    DATABASES = {"default": default_database}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/accounts/login/"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-client-identifier",
]


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "oauth2_provider.backends.OAuth2Backend",
)

OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 300,
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 300,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 6000,
    "ROTATE_REFRESH_TOKEN": True,
    "SCOPES": {
        "read": "Read scope",
        "write": "Write scope",
        "groups": "Access your groups",
    },
}


BASE_URL = env("BASE_URL")
CLIENT_SECRET = env("CLIENT_SECRET")
CLIENT_ID = env("CLIENT_ID")
CLIENT_URL = env("CLIENT_URL")
MAILTRAP_TOKEN = env("MAILTRAP_TOKEN")
CLIENT_IDENTIFIER = env("CLIENT_IDENTIFIER")
