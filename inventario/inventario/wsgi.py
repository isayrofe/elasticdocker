"""
WSGI config for inventario project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path
from django.conf import settings

#BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario.settings.development')

application = get_wsgi_application()
#application = WhiteNoise(application, settings.STATIC_ROOT)

#application.add_files("/staticfiles", prefix="staticfiles/")