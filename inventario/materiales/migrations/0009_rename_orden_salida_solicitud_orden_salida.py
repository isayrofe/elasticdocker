# Generated by Django 5.0.1 on 2024-02-27 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('materiales', '0008_remove_orden_salida_solicitud_solicitud_orden_salida'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solicitud',
            old_name='Orden_salida',
            new_name='orden_salida',
        ),
    ]
