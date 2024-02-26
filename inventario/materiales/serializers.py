from datetime import timezone
from django.contrib.auth.models import Group, UserManager
from .models import Almacen, Catalogo, Detalles_Solicitud, Detalle_Salida, Detalle_Vale, Orden_Entrada, Detalle_Entrada, Orden_Salida, Solicitud, Unidad, Proveedor, Vale, CustomUser
from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = '__all__'

class CatalogoSerializer(serializers.ModelSerializer):
    tipo_unidad = serializers.CharField(source='unidad.nombre', read_only=True)
    class Meta:
        model = Catalogo
        fields = ['id','nombre', 'imagen', 'descripcion', 'unidad','tipo_unidad']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

class AlmacenSerializer(serializers.ModelSerializer):
    nombre_articulo = serializers.CharField(source='articulo', read_only=True)
    tipo_unidad = serializers.CharField(source='articulo.unidad', read_only=True)
    imagen = serializers.CharField(source='articulo.imagen', read_only=True)
    class Meta:
        model = Almacen
        fields = ['articulo','fecha_actualizacion','existencia','nombre_articulo','tipo_unidad','imagen']
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    


class DetalleEntradaSerializer(serializers.ModelSerializer):
    nombre_articulo = serializers.CharField(source='almacen.articulo.nombre', read_only=True)
    tipo_unidad = serializers.CharField(source='almacen.articulo.unidad', read_only=True)
    id_proveedor = serializers.IntegerField(source='orden.proveedor.id', required=False)
    fecha_orden = serializers.DateField(source='orden.fecha_orden', required=False)
    class Meta:
        model = Detalle_Entrada
        fields = ['id','almacen', 'cantidad','nombre_articulo','tipo_unidad','id_proveedor', 'fecha_orden']

class OrdenEntradaSerializer(serializers.ModelSerializer):
    detalles_entrada = DetalleEntradaSerializer(many=True)

    class Meta:
        model = Orden_Entrada
        fields = ['id','fecha_orden', 'proveedor', 'descripcion', 'detalles_entrada']
        
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_entrada')  # Use the default related name
        orden_entrada = Orden_Entrada.objects.create(**validated_data)
        for detalle_data in detalles_data:
            Detalle_Entrada.objects.create(orden=orden_entrada, **detalle_data)
        return orden_entrada

class DetalleSalidaSerializer(serializers.ModelSerializer):
    nombre_articulo = serializers.CharField(source='almacen.articulo.nombre',required=False, read_only=True)
    tipo_unidad = serializers.CharField(source='almacen.articulo.unidad', required=False, read_only=True)
    fecha_orden = serializers.DateField(source='orden.fecha_orden', required=False, read_only=True)
    class Meta:
        model = Detalle_Salida
        fields = ['id','almacen', 'cantidad', 'nombre_articulo', 'tipo_unidad', 'fecha_orden']

class OrdenSalidaSerializer(serializers.ModelSerializer):
    detalles_salida = DetalleEntradaSerializer(many=True)
    class Meta:
        model = Orden_Salida
        fields = ['id','fecha_orden', 'descripcion', 'detalles_salida', 'solicitud']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_salida')  # Use the default related name
        orden_salida = Orden_Salida.objects.create(**validated_data)
        for detalle_data in detalles_data:
            Detalle_Salida.objects.create(orden=orden_salida, **detalle_data)
        return orden_salida

class DetalleSolicitudSerializer(serializers.ModelSerializer):
    nombre_articulo = serializers.CharField(source='catalogo.nombre', read_only=True, required=False)
    tipo_unidad = serializers.CharField(source='producto.unidad.nombre', read_only=True)
    id_Detalle_Solicitud = serializers.IntegerField(source='id', read_only=True)
    producto_personalizado = serializers.CharField(source='personalizado', required=False)
    class Meta:
        model = Detalles_Solicitud
        fields = ['id_Detalle_Solicitud','catalogo', 'producto_personalizado', 'cantidad', 'nombre_articulo', 'tipo_unidad']
        #fields = '__all__'

class SolicitudSerializer(serializers.ModelSerializer):
    detalles_solicitud = DetalleSolicitudSerializer(many=True)
    id_solicitud = serializers.IntegerField(source='id', required=False, read_only=True)
    

    class Meta:
        model = Solicitud
        fields = ['id_solicitud','fecha','tipo', 'estado', 'descripcion', 'detalles_solicitud']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_solicitud')  # Use the default related name
        solicitud = Solicitud.objects.create(**validated_data)
        for detalle_data in detalles_data:
            Detalles_Solicitud.objects.create(solicitud=solicitud, **detalle_data)
        return solicitud
    
    def update(self, instance, validated_data):
        instance.fecha = validated_data.get('fecha', instance.fecha)
        instance.tipo = validated_data.get('tipo', instance.tipo)
        instance.estado = validated_data.get('estado', instance.estado)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)

        detalles_data = validated_data.get('detalles_solicitud')
        if detalles_data:
            # Creamos un diccionario con los ID de los detalles proporcionados
            detalles_ids = {item['id_Detalle_Solicitud'] for item in detalles_data if 'id_Detalle_Solicitud' in item}

            # Actualizamos los detalles existentes y eliminamos los detalles que no están en la lista de detalles proporcionados
            for detalle in instance.detalles_solicitud.all():
                if detalle.id not in detalles_ids:
                    detalle.delete()
                # else:
                #     detalle_data = next((item for item in detalles_data if item.get('catalogo') == detalle.catalogo), None)
                #     if detalle_data:
                #         detalle.cantidad = detalle_data.get('cantidad', detalle.cantidad)
                #         detalle.save()

            # Creamos nuevos detalles para los detalles que no existen actualmente
            for detalle_data in detalles_data:
                if 'id' not in detalle_data:
                    Detalles_Solicitud.objects.create(solicitud=instance, **detalle_data)

        instance.save()
        return instance

class DetalleValeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Vale
        fields = ['vale', 'producto', 'personalizado', 'cantidad']

class ValeSerializer(serializers.ModelSerializer):
    detalles_vale = DetalleValeSerializer(many=True)
    class Meta:
        model = Vale
        fields = ['fecha', 'descripcion', 'detalles_vale']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_vale')  # Use the default related name
        vale = Vale.objects.create(**validated_data)
        for detalle_data in detalles_data:
            Detalle_Vale.objects.create(vale=vale, **detalle_data)
        return vale
    
class MovimientosSerializer(serializers.Serializer):
    tipo_movimiento = serializers.CharField()
    detalle = DetalleEntradaSerializer()  # Use DetalleEntradaSerializer or DetalleSalidaSerializer based on your requirements

class MovimientosAlmacenSerializer(serializers.Serializer):
    almacen__articulo__nombre=serializers.CharField()
    id_catalogo=serializers.IntegerField()
    #nombre_articulo = serializers.CharField()
    cantidad_total_entrada = serializers.IntegerField()
    ultima_actualizacion = serializers.DateField()
    #detalle = DetalleEntradaSerializer()

class MovimientosAlmacenQuerySerializer(serializers.Serializer):
    nombre_articulo = serializers.CharField()  # Cambiado de "nombre" a "nombre_articulo"
    id_catalogo = serializers.IntegerField()
    cantidad_total_entrada = serializers.DecimalField(max_digits=10, decimal_places=2)  # Ajusta los tipos de datos según tu modelo
    cantidad_total_salida = serializers.DecimalField(max_digits=10, decimal_places=2)  # Ajusta los tipos de datos según tu modelo
    ultima_actualizacion = serializers.DateField()
    cantidad_final = serializers.DecimalField(max_digits=10, decimal_places=2)  # Ajusta los tipos de datos según tu modelo

class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'