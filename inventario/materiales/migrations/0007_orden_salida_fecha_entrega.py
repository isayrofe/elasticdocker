# Generated by Django 5.0.1 on 2024-02-27 20:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiales', '0006_solicitud_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden_salida',
            name='fecha_entrega',
            field=models.DateField(default=datetime.date(2024, 2, 27)),
        ),
    ]