from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Keep Django's existing loggers
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",  # Reduce verbosity (DEBUG -> WARNING)
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "loki": {
            "level": "INFO",
            "class": "logging.NullHandler",  # Avoid double logging from Django
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",  # Reduce verbosity
            "propagate": False,  # Prevent duplicate logging
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "my_app": {
            "handlers": ["loki"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#In production (when DEBUG = False), Django requires ALLOWED_HOSTS to be non-empty, or it will reject all requests with a 400 Bad Request error.

ALLOWED_HOSTS = [

    "portfolio-backend-h6hf.onrender.com",  # Your backend domain
    "localhost",  # Allow local development
    "127.0.0.1",
    "https://shivam-portfoliio.vercel.app/"
]
#This restricts the Host header to your backend’s domain, preventing spoofing attempts from other domains.
#Note: You don’t include the frontend domain here—it’s about the backend’s identity.
#The browser will block any cross-origin requests from domains not in this list
# Application definition

# Allow specific frontend origins
CORS_ALLOWED_ORIGINS = [
    "https://shivam-portfoliio.vercel.app",
    "http://localhost:5500"
]

CORS_ALLOW_HEADERS = ["session_id","x-csrftoken", "Content-Type", "Authorization"]  # Allow API key in headers
CORS_ALLOW_METHODS = [
    "GET",     # Fetch data
    "POST",    # Submit data
    "OPTIONS", # Preflight requests (required for CORS)
    # "PATCH",   # Partial updates (optional, if needed)
]

CORS_ALLOW_CREDENTIALS = True  # frontend needs to send cookies or authentication credentials

#Optional: Force JSON rendering
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbackend',
    'corsheaders',
    'rest_framework'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portfoliobackend.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'portfoliobackend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # IST timezone
USE_TZ = True  # Django stores time in UTC but converts to TIME_ZONE
USE_I18N = True
STATIC_URL = 'static/'
# Define the directories where static files will be collected from
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
