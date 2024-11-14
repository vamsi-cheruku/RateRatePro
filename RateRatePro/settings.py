import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-j7-x)@b=5yrbz(+c&*+&f(2d1k$)=*a530uhh#!@%4m)w-5jfe"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['3.88.219.13','34.205.32.248', 'localhost', '127.0.0.1', '54.211.21.255']

# To neglect the slash at the end of endpoint
# APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "RateRatePro",
    "rest_framework",
    'django_elasticsearch_dsl',
    'corsheaders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "RateRatePro.urls"

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

WSGI_APPLICATION = "RateRatePro.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        
        #! MySQL crediantial for localhost
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_rateratepro',  # Your test database
        'USER': 'root',
        'PASSWORD': 'Cheruku@0627',
        'HOST': 'localhost',  # Correct for GitHub Actions, or use '127.0.0.1'
        'PORT': '3307',  # The port mapped in the Docker container
        
        #! MySQL credintials for AWS
        # 'USER': 'admin',
        # 'PASSWORD': 'rootadmin',
        # 'HOST': 'rateratepro.cr6qy22gqg7f.us-east-1.rds.amazonaws.com',  # e.g., the hostname provided by the MySQL service
        # 'PORT': '3306',  # default MySQL port
        
        
    }
}

#Elastic search engine configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'  # Replace with your Elasticsearch host if different
    },
    
    #! AWS Elasticsearch credentials 
    # 'default' : {
    #     'hosts' : 'https://search-rateratepro-v6v5ugewbfvijd7akccrma7pry.aos.us-east-1.on.aws'
    # }
}

OPENSEARCH_HOST = 'https://your-opensearch-domain'

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

OPTIONS = {
    'unix_socket': '/var/run/mysqld/mysqld.sock',  # Update with actual socket path if different
}
