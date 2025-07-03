

from pathlib import Path
from decouple import config
import os
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_extensions',
    "rest_framework",
    "rest_framework_simplejwt",
    "core",  # Add your app
    "rbac",
    "master",
    "payment",
    "organization",
    "property",
    "booking",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",  # Add providers you need
    "allauth.socialaccount.providers.facebook",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "corsheaders",
]
SITE_ID = 1  # Ensure this matches your Django Site in Admin Panel
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

REST_FRAMEWORK = {
    "DEFAULT_METADATA_CLASS": "core.metadata.CustomUIMetadata",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.CustomPagination',
    'PAGE_SIZE': 20,  # Default page size
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",  # ✅ Add this
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ]
    #'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.SearchFilter']

}

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False  # We are using email instead of username
LOGIN_URL = "/api/login/"


from datetime import timedelta

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False, # refresh token stays valid until it expires
    "BLACKLIST_AFTER_ROTATION": True, # Tokens won’t get auto-invalidated
    "AUTH_HEADER_TYPES": ("Bearer",),
}



MIDDLEWARE = [
    # Audit Logging
    #"core.middlewares.APILoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
LOG_QUERY = config("LOG_QUERY", default=False,cast=bool)
if LOG_QUERY:
    import logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',  # Log all queries
                'handlers': ['console'],
            },
        },
    }

ROOT_URLCONF = "homerun.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
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

WSGI_APPLICATION = "homerun.wsgi.application"
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
JAZZMIN_SETTINGS = {
    "site_title": "Homerun Admin",
    "site_header": "Homerun Admin",
    "site_brand": "Homerun Admin",
    "welcome_sign": "Welcome to Homerun",
    "show_sidebar": True,  # Hide or show the sidebar
    "navigation_expanded": True,  # Keep the sidebar expanded by default
    # "theme": "cyborg",  # Change theme (e.g., flatly, cyborg, lumen, lux)
    "site_logo": "images/direct-logo.svg",  # Path relative to STATICFILES
    "login_logo": "images/direct-logo.svg",  # Logo on the login page
    "site_brand": "My Custom Admin",  # Text next to the logo
    #"custom_css": "css/custom.css", TO override CSS for Dilip


}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "rbac.DirectUser"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["email", "profile"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for testing
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]  # Allow all headers

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # For testing (prints emails in the console)



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For testing
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

REST_AUTH_SERIALIZERS = {
    'PASSWORD_RESET_SERIALIZER': 'rbac.serializers.CustomPasswordResetSerializer',
    'PASSWORD_RESET_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetSerializer',
    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetConfirmSerializer',
}
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# For production, use SMTP settings:
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL=EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="no-reply@example.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
SECRET_KEY = config("SECRET_KEY")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
CURRENT_DIRECT_LOGIN_URL = config("CURRENT_DIRECT_LOGIN_URL", default="https://staging.getdirect.io/authentications/sessions")
SOCIAL_AUTH_GOOGLE_CLIENT_ID = config("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
SECRET_KEY = config("SECRET_KEY")
USE_POSTGRES = config("USE_POSTGRES", default=False, cast=bool)



if USE_POSTGRES:
    PG_DB_NAME = config("PG_DB_NAME")
    PG_USER = config("PG_USER")
    PG_PASSWORD = config("PG_PASSWORD")
    PG_HOST = config("PG_HOST")
    PG_PORT = config("PG_PORT", cast=int)
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': PG_DB_NAME,
            'USER': PG_USER,
            'PASSWORD': PG_PASSWORD,
            'HOST': PG_HOST,
            'PORT': PG_PORT,
        }
    }



# Caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{os.getenv('REDIS_PASSWORD', '')}@localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Elasticsearch
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': f"http://localhost:9200"
    },
}


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



