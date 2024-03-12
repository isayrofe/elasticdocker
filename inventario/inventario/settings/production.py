from .base import *
from ..logging import *

import os
from dotenv import load_dotenv


load_dotenv(Path.joinpath(BASE_DIR,'.env'))

#SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-@!g4w)br&_%@ezu4r1z+&g+l0o7j3*2-q@bg!=%zqu#%q*n5dx'
SECRET_KEY = os.environ.get('SECRET_KEY')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATIC_URL = 'staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')




#SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['http://localhost:8080']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

ELASTIC_APM = {
    'SERVICE_NAME': 'django-inventarios',
    'SERVER_URL': 'http://fleet-server:8200',
    'SECRET_TOKEN': 'supersecrettoken',
    'ENVIRONMENT': 'development',
}

AUTH_USER_MODEL = 'materiales.CustomUser'
