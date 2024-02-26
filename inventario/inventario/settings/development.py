from .base import *

#SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@!g4w)br&_%@ezu4r1z+&g+l0o7j3*2-q@bg!=%zqu#%q*n5dx'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Log anonymous actions?
ACTIVITYLOG_ANONYMOUS = True

# Update last activity datetime in user profile. Needs updates for user model.
ACTIVITYLOG_LAST_ACTIVITY = True

# Only this methods will be logged
ACTIVITYLOG_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

#SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CSRF_TRUSTED_ORIGINS = [
     'http://localhost:4500',
     'http://localhost:4200',
     'http://172.80.13.6:4500',
     'http://172.80.13.6',
     'http://192.168.20.129',
     'http://172.80.13.4',
     'http://172.80.13.4:4200',
     'http://192.68.33.11',
     ]

CSRF_COOKIE_SECURE = False

CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False  # this is the default, and should be kept this way
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'X-CSRFToken'



CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "X-XSRF-TOKEN",
    "X-CSRFToken",
    "X-SRFToken",
    "Cookie",
    "csrfmiddlewaretoken",
    "csrftoken",
)

ALLOWED_HOSTS = ['*']


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': 'inventarios',
       'USER': 'postgres',
       'PASSWORD': 'isay',
       'HOST': '172.80.13.4',   
       'PORT': '5432',
   },
   'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "test_db.sqlite3",
    },
}

ELASTIC_APM = {
    'SERVICE_NAME': 'django-inventarios',
    'SERVER_URL': 'http://192.168.33.11:8200',
    'SECRET_TOKEN': 'supersecrettoken',
    'ENVIRONMENT': 'development',
    'DEBUG': True
}

AUTH_USER_MODEL = 'materiales.CustomUser'
