from django.db import models
from django.forms import ValidationError
from django_resized import ResizedImageField
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
# class UserActivityLog(models.Model):
#     #user = models.ForeignKey(User, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(default=timezone.now)
#     action = models.CharField(max_length=255)

#     def __str__(self):
#         return f"{self.user.username} - {self.action} - {self.timestamp}"


class Unidad(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

# Create your models here.
class Catalogo(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = ResizedImageField(size=[300, 300], quality=100, upload_to="catalogo", blank=True)
    descripcion = models.CharField(max_length=250, default="")
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.nombre


class Almacen(models.Model):
    articulo = models.OneToOneField(Catalogo, on_delete=models.CASCADE, default=0)
    fecha_actualizacion = models.DateTimeField(default=timezone.now)
    existencia = models.IntegerField()

    

class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.CharField(max_length=50)
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Orden_Entrada(models.Model):
    fecha_orden = models.DateField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=400, default="")

class Detalle_Entrada(models.Model):
    orden = models.ForeignKey(Orden_Entrada, related_name='detalles_entrada', on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, default=0)
    cantidad = models.IntegerField()

    
class CustomUser(AbstractUser):
    area = models.CharField(max_length=50, default="")
    modulo = models.CharField(max_length=50, default="")
    persona_nombre = models.CharField(max_length=50, default="")

class Solicitud(models.Model):
    fecha = models.DateField()
    tipo = models.CharField(max_length=50, default="requisicion")
    descripcion = models.CharField(max_length=400, default="")
    estado = models.CharField(max_length=50, default="pendiente")
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    
class Orden_Salida(models.Model):
    fecha_orden = models.DateField()
    fecha_entrega = models.DateField(default=timezone.now().date())
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, default=0)
    descripcion = models.CharField(max_length=400, default="")
    def __str__(self):
        return self.solicitud.fecha
    
class Detalles_Solicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, related_name='detalles_solicitud', on_delete=models.CASCADE)
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE, default=0)
    personalizado = models.CharField(max_length=100, null=True, blank=True)
    cantidad = models.IntegerField()

    def clean(self):
        if not self.producto and not self.nombre_producto_personalizado:
            raise ValidationError("Debes proporcionar un producto del catálogo o un nombre personalizado.")

        if self.producto and self.nombre_producto_personalizado:
            raise ValidationError("Solo puedes proporcionar un producto del catálogo o un nombre personalizado, no ambos.")


class Detalle_Salida(models.Model):
    orden = models.ForeignKey(Orden_Salida, related_name='detalles_salida', on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, default=0)
    cantidad = models.IntegerField()

class Vale(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=400, default="")
    estado = models.CharField(max_length=50, default="pendiente")

class Detalle_Vale(models.Model):
    vale = models.ForeignKey(Vale, related_name='detalles_vale', on_delete=models.CASCADE)
    producto = models.ForeignKey(Catalogo, on_delete=models.CASCADE, null=True, blank=True)
    personalizado = models.CharField(max_length=100, null=True, blank=True)
    cantidad = models.IntegerField()




