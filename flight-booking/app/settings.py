"""
Django settings for flightbooking project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
import environ

import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env('.env')

# False if not in os.environ
DEBUG = env('DEBUG')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    'flight-booking-lms.herokuapp.com/'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_celery_beat',
    'django_celery_results',

    'rest_framework',

    'cloudinary',

    'corsheaders',
    'django_nose',

    'app',

    'app.accounts',
    'app.helpers',
    'app.uploads',
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

ROOT_URLCONF = 'app.urls'

REST_FRAMEWORK = {
    # When you enable API versioning, the request.version attribute will
    # contain a string that corresponds to the version requested in the
    # incoming client request.
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER': 'app.helpers.exceptions.handle_exceptions',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
IS_TEST = (len(sys.argv) > 1 and sys.argv[1] == 'test') or env(
    'CIRCLECI', default=False)
if IS_TEST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST_NAME': ':memory:',
        }
    }
    DEBUG = False
else:
    DATABASES = {
        'default': {
            'ENGINE': 'mysql.connector.django',
            'HOST': env('MYSQL_DB_HOST'),
            'USER': env('MYSQL_USER'),
            'NAME': env('MYSQL_DATABASE'),
            'PASSWORD': env('MYSQL_PASSWORD'),
            'OPTIONS': {
                'autocommit': True,
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--verbosity=2',
    '--cover-erase',
    '--with-xunit',
    '--xunit-file=xunittest.xml',
    '--with-coverage',
    '--cover-package=app',
    '--cover-inclusive',
]

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': 'flight-booking',
    'JWT_ALLOW_REFRESH': True

}

CELERY_TIMEZONE = env('CELERY_TIMEZONE', default='UTC')
CELERY_TASK_SERIALIZER = env('CELERY_TASK_SERIALIZER', default='json')
CELERY_RESULT_SERIALIZER = env('CELERY_RESULT_SERIALIZER', default='json')
CELERY_ACCEPT_CONTENT = ['json', 'application/text']
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=None)
if CELERY_BROKER_URL is None:
    CELERY_BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=env('RABBIT_ENV_USER', default='guest'),
        password=env('RABBIT_ENV_RABBITMQ_PASS', default='guest'),
        hostname=env('RABBIT_HOSTNAME', default='localhost'),
        vhost=env('RABBIT_ENV_VHOST', default=''))

# add heartbeat
BROKER_HEARTBEAT = '?heartbeat=30'
if not CELERY_BROKER_URL.endswith(BROKER_HEARTBEAT):
    CELERY_BROKER_URL += BROKER_HEARTBEAT

CELERY_RESULT_BACKEND = env('REDIS_URL', default='rpc://')

if not IS_TEST:
    django_heroku.settings(locals())
