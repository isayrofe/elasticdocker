# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Detalle_Entrada, Detalle_Salida, Almacen, Catalogo
from django.core.exceptions import ValidationError
from django.utils import timezone

@receiver(post_save, sender=Detalle_Entrada)
@receiver(post_delete, sender=Detalle_Entrada)
def actualizar_existencia_entrada(sender, instance, **kwargs):
    almacen = instance.almacen
    cantidad = instance.cantidad
    almacen.existencia += cantidad
    almacen.fecha_actualizacion = timezone.now()
    
    if almacen.existencia < 0:
        raise ValidationError("La existencia del almacén no puede ser negativa.")

    almacen.save()

@receiver(post_save, sender=Detalle_Salida)
@receiver(post_delete, sender=Detalle_Salida)
def actualizar_existencia_salida(sender, instance, **kwargs):
    almacen = instance.almacen
    cantidad = instance.cantidad
    almacen.existencia -= cantidad
    almacen.fecha_actualizacion = timezone.now()
    if almacen.existencia < 0:
        raise ValidationError("La existencia del almacén no puede ser negativa.")

    almacen.save()

@receiver(post_save, sender=Catalogo)
def create_almacen(sender, instance, created, **kwargs):
    if created:
        Almacen.objects.create(articulo=instance, existencia=0)


