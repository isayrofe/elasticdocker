#!/bin/bash

#echo "Collecting static files..."
#python manage.py collectstatic --noinput --settings=inventario.settings.production
echo "Starting Django server..."

echo "Migrating database..."
python manage.py makemigrations --no-input --settings=inventario.settings.production

echo "Migrating database..."
python manage.py migrate --settings=inventario.settings.production

# Collect static files
#echo "Collecting static files..."
#python manage.py collectstatic --no-input --settings=inventario.settings.production

python manage.py shell --settings=inventario.settings.production <<EOF
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME')
except User.DoesNotExist:
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
EOF


echo "Starting server..."
gunicorn --env DJANGO_SETTINGS_MODULE=inventario.settings.production inventario.wsgi:application --bind 0.0.0.0:8000