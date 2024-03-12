import datetime
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .backend import external_token_required
from django.db import connection
from django.utils.decorators import method_decorator
from .serializers import (
    AlmacenSerializer, CatalogoSerializer, MovimientosAlmacenSerializer, OrdenEntradaSerializer,
    OrdenSalidaSerializer, SolicitudCombinadaSerializer, SolicitudSerializer, SolicitudesSerializer, UnidadSerializer,
    ProveedorSerializer, ValeSerializer, DetalleEntradaSerializer,
    DetalleSalidaSerializer, MovimientosSerializer, MovimientosAlmacenQuerySerializer,
    UsuariosSerializer, DetalleSolicitudSerializer
)
from .models import (
    Almacen, Catalogo, Orden_Entrada, Orden_Salida,
    Solicitud, Unidad, Proveedor, Vale, Detalle_Entrada, Detalle_Salida, CustomUser
)
from django.db.models import F, Value, Sum, Max, Min, IntegerField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
import logging


grupos = {
    1: "Administradores",
    2: "Supervisores",
    3: "Operadores",
}

logger = logging.getLogger("materiales")

def obtener_info_solicitud(request,self):
    
    usuario = self.user.username if self.user.is_authenticated else 'Anónimo'
    try:
        dispositivo = request.META.get('HTTP_USER_AGENT', 'Desconocido')
        ip = request.META.get('REMOTE_ADDR', 'Desconocido')
    except:
        dispositivo = 'Desconocido'
        ip = 'Desconocido'
    # dispositivo = request.META.get('HTTP_USER_AGENT', 'Desconocido')
    # ip = request.META.get('REMOTE_ADDR', 'Desconocido')
    return usuario, dispositivo, ip

def registrar_cambios(instance, request, logger, objeto_name, pk, serializer, self):
    # Guardar los datos actuales antes de la actualización
    datos_anteriores = serializer(instance).data
    # Obtener información sobre el usuario, el dispositivo y la IP utilizando la función de utilidad
    usuario, dispositivo, ip = obtener_info_solicitud(request, self)
    try:
        datos_nuevos = request.data
    except:
        datos_nuevos = request
    #datos_nuevos = request.data
    # Comparar los datos y registrar los cambios
    cambios = {}
    for key, value in datos_nuevos.items():
        if value != datos_anteriores.get(key):
            cambios[key] = {
                'anterior': datos_anteriores.get(key),
                'actual': value
            }
    
    if cambios:
        mensaje = f'{objeto_name} actualizado con id {pk}: {cambios}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}'
        logger.info(mensaje)

    return cambios

def crear_registro(serializer, request, self):
    # Obtener información sobre el usuario, el dispositivo y la IP utilizando la función de utilidad
    usuario, dispositivo, ip = obtener_info_solicitud(request,self)
    logger.info(f'Nuevo proveedor creado: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
    
    

def es_miembro_grupo(request, group_name):
    return request.user.groups.filter(name=grupos[group_name]).exists()


def filtrar_por_producto(queryset, producto_id):
    return queryset.filter(almacen__articulo__id=producto_id)


def filtrar_por_fecha(queryset, fecha):
    return queryset.filter(orden__fecha_orden=fecha)


def filtrar_por_rango_fechas(queryset, fecha_inicio, fecha_fin):
    return queryset.filter(orden__fecha_orden__range=[fecha_inicio, fecha_fin])


def limitar_registros(queryset, cantidad_registros):
    return queryset[:int(cantidad_registros)]


def asignar_tipo_movimiento(detalles, tipo_movimiento):
    return [{'tipo_movimiento': tipo_movimiento, 'detalle': detalle} for detalle in detalles]
#def asignar_tipo_movimiento(detalles, tipo):
#    return [{'tipo_movimiento': tipo, 'detalle': detalle} for detalle in detalles]


#@method_decorator(external_token_required, name='dispatch')
class ProveedorViewSet(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nuevo proveedor creado: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class ProveedorUpdateViewSet(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request, logger, 'Proveedor', kwargs['pk'], ProveedorSerializer, self)
        return response
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'Proveedor eliminado con id {kwargs["pk"]}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class UnidadViewSet(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request,self)
        logger.info(f'Nueva Unidad creada: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response
    


#@method_decorator(external_token_required, name='dispatch')
class UnidadUpdateViewSet(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request.data, logger, 'Unidad', kwargs['pk'], UnidadSerializer, self)
        return response
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'Unidad eliminado con id {kwargs["pk"]}')
        return response


#@method_decorator(external_token_required, name='dispatch')
class CatalogoViewSet(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Catalogo.objects.all()
    serializer_class = CatalogoSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nueva Catalogo creada: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class CatalogoUpdateViewSet(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Catalogo.objects.all()
    serializer_class = CatalogoSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request.data, logger, 'Catalogo', kwargs['pk'], CatalogoSerializer, self)
        return response
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'Catalogo eliminado con id {kwargs["pk"]}')
        return response
    


#@method_decorator(external_token_required, name='dispatch')
class AlmacenViewSet(generics.ListAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    #queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    def get_queryset(self):
        queryset = Almacen.objects.all()
        return self.filtrar_y_limitar(queryset)

    def filtrar_y_limitar(self, queryset):
        producto_id = self.request.query_params.get('producto_id', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        if producto_id:
            queryset = queryset.filter(articulo__id=producto_id)

        if cantidad_registros:
            queryset = queryset[:int(cantidad_registros)]

        return queryset
    

#@method_decorator(external_token_required, name='dispatch')
class AlmacenUpdateViewSet(generics.RetrieveAPIView):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        cambios = registrar_cambios(instance, request.data, logger, 'Almacen', kwargs['pk'], AlmacenSerializer)
        return response

#@method_decorator(external_token_required, name='dispatch')
class OrdenEntradaListCreateView(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Orden_Entrada.objects.all()
    serializer_class = OrdenEntradaSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request,self)
        logger.info(f'Nueva Orden Entrada creada: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class OrdenEntradaUpdateView(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Orden_Entrada.objects.all()
    serializer_class = OrdenEntradaSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request.data, logger, 'Orden_Entrada', kwargs['pk'], OrdenEntradaSerializer, self)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'Orden Entrada eliminada con id {kwargs["pk"]}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class OrdenSalidaListCreateView(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Orden_Salida.objects.all()
    serializer_class = OrdenSalidaSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nueva Orden Salida creada: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class OrdenSalidaUpdateView(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Orden_Salida.objects.all()
    serializer_class = OrdenSalidaSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request.data, logger, 'Orden_Salida', kwargs['pk'], OrdenSalidaSerializer, self)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        logger.info(f'Orden Salida eliminada con id {kwargs["pk"]}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class SolicitudListCreateView(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.user  # Añadir el usuario al contexto del serializador
        return context
    
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nueva Solicitud creada: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class SolicitudUpdateView(generics.RetrieveUpdateDestroyAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)
        # Obtener información sobre el usuario y el dispositivo
        cambios = registrar_cambios(instance, request.data, logger, 'Solicitud', kwargs['pk'], SolicitudSerializer, self)
        return response

#@method_decorator(external_token_required, name='dispatch')
class ValeListCreateView(generics.ListCreateAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    queryset = Vale.objects.all()
    serializer_class = ValeSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nuevo vale creado: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response

#@method_decorator(external_token_required, name='dispatch')
class MovimientosEntradaView(generics.ListAPIView):
    serializer_class = DetalleEntradaSerializer

    def get_queryset(self):
        queryset = Detalle_Entrada.objects.all()
        return self.filtrar_y_limitar(queryset)

    def filtrar_y_limitar(self, queryset):
        producto_id = self.request.query_params.get('producto_id', None)
        fecha = self.request.query_params.get('fecha', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        if producto_id:
            queryset = filtrar_por_producto(queryset, producto_id)

        if fecha:
            queryset = filtrar_por_fecha(queryset, fecha)

        if fecha_inicio and fecha_fin:
            queryset = filtrar_por_rango_fechas(queryset, fecha_inicio, fecha_fin)

        if cantidad_registros:
            queryset = limitar_registros(queryset, cantidad_registros)

        return queryset

#@method_decorator(external_token_required, name='dispatch')
class MovimientosSalidaView(generics.ListAPIView):
    serializer_class = DetalleSalidaSerializer

    def get_queryset(self):
        queryset = Detalle_Salida.objects.all()
        return self.filtrar_y_limitar(queryset)

    def filtrar_y_limitar(self, queryset):
        producto_id = self.request.query_params.get('producto_id', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        fecha = self.request.query_params.get('fecha', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        if producto_id:
            queryset = filtrar_por_producto(queryset, producto_id)

        if fecha_inicio and fecha_fin:
            queryset = filtrar_por_rango_fechas(queryset, fecha_inicio, fecha_fin)

        if fecha:
            queryset = filtrar_por_fecha(queryset, fecha)

        if cantidad_registros:
            queryset = limitar_registros(queryset, cantidad_registros)
        print(queryset)
        
        
        return queryset

#@method_decorator(external_token_required, name='dispatch')
class MovimientosView(generics.ListAPIView):
    serializer_class = MovimientosSerializer

    def get_queryset(self):
        detalles_entrada = Detalle_Entrada.objects.all()
        detalles_salida = Detalle_Salida.objects.all()
        return self.filtrar_y_limitar(detalles_entrada, detalles_salida)

    def filtrar_y_limitar(self, detalles_entrada, detalles_salida):
        producto_id = self.request.query_params.get('producto_id', None)
        fecha = self.request.query_params.get('fecha', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        if producto_id:
            detalles_entrada = filtrar_por_producto(detalles_entrada, producto_id)
            detalles_salida = filtrar_por_producto(detalles_salida, producto_id)

        if fecha:
            detalles_entrada = filtrar_por_fecha(detalles_entrada, fecha)
            detalles_salida = filtrar_por_fecha(detalles_salida, fecha)

        if fecha_inicio and fecha_fin:
            detalles_entrada = filtrar_por_rango_fechas(detalles_entrada, fecha_inicio, fecha_fin)
            detalles_salida = filtrar_por_rango_fechas(detalles_salida, fecha_inicio, fecha_fin)

        if cantidad_registros:
            detalles_entrada = limitar_registros(detalles_entrada, cantidad_registros)
            detalles_salida = limitar_registros(detalles_salida, cantidad_registros)

        detalles_entrada = asignar_tipo_movimiento(detalles_entrada, 'entrada')
        detalles_salida = asignar_tipo_movimiento(detalles_salida, 'salida')

        queryset = detalles_entrada + detalles_salida
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

# class MovimientosAlmacenView(generics.ListAPIView):
#     serializer_class = MovimientosAlmacenSerializer

#     def get_queryset(self):
#         detalles_entrada = Detalle_Entrada.objects.values('almacen__articulo__nombre').annotate(
#             #nombre_articulo='almacen__articulo__nombre',
#             id_catalogo = Min('almacen_id'),
#             cantidad_total_entrada=Sum('cantidad'),
#             ultima_actualizacion=Max("orden__fecha_orden")
#         )

#         detalles_salida = Detalle_Salida.objects.values('almacen__articulo__nombre').annotate(
#             #nombre_articulo='almacen__articulo__nombre',
#             id_catalogo = Min('almacen_id'),
#             cantidad_total_salida=Sum('cantidad'),
#             ultima_actualizacion=Max("orden__fecha_orden")
#         )
#         print(connection.queries)
#         producto_id = self.request.query_params.get('producto_id', None)
#         fecha = self.request.query_params.get('fecha', None)
#         fecha_inicio = self.request.query_params.get('fecha_inicio', None)
#         fecha_fin = self.request.query_params.get('fecha_fin', None)
#         cantidad_registros = self.request.query_params.get('cantidad_registros', None)

#         detalles_entrada = self.filtrar_por_producto_fecha_y_limitar(detalles_entrada, producto_id, fecha, fecha_inicio, fecha_fin, cantidad_registros)
#         detalles_salida = self.filtrar_por_producto_fecha_y_limitar(detalles_salida, producto_id, fecha, fecha_inicio, fecha_fin, cantidad_registros)

       
#         # Realizar una unión de los resultados de entrada y salida
#         queryset = detalles_entrada.union(detalles_salida)

#         return queryset

#     def filtrar_por_producto_fecha_y_limitar(self, queryset, producto_id, fecha, fecha_inicio, fecha_fin, cantidad_registros):
#         if producto_id:
#             queryset = queryset.filter(almacen__articulo__id=producto_id)

#         if fecha:
#             queryset = queryset.filter(orden__fecha_orden=fecha)

#         if fecha_inicio and fecha_fin:
#             queryset = queryset.filter(orden__fecha_orden__range=[fecha_inicio, fecha_fin])

#         if cantidad_registros:
#             queryset = queryset[:int(cantidad_registros)]

#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response(serializer.data)
#@method_decorator(external_token_required, name='dispatch')

class UsuariosView(generics.ListAPIView):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    queryset = CustomUser.objects.all()
    serializer_class = UsuariosSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        usuario, dispositivo, ip = obtener_info_solicitud(request, self)
        logger.info(f'Nuevo usuario creado: {request.data}. Usuario: {usuario}, Dispositivo: {dispositivo}, IP: {ip}')
        return response
    
class MovimientosAlmacenView(generics.ListAPIView):
    serializer_class = MovimientosAlmacenQuerySerializer

    def get_queryset(self):
        producto_id = self.request.query_params.get('producto_id', None)
        fecha = self.request.query_params.get('fecha', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        # Consulta SQL personalizada para obtener el resultado deseado
        query = """
            SELECT
                nombre_articulo,
                id_catalogo,
                SUM(cantidad_total_entrada) AS cantidad_total_entrada,
                SUM(cantidad_total_salida) AS cantidad_total_salida,
                MAX(ultima_actualizacion) AS ultima_actualizacion,
                (
                    SUM(cantidad_total_entrada) - SUM(cantidad_total_salida)
                ) AS cantidad_final
                FROM
                (
                    select
                    PE.nombre as nombre_articulo,
                    DE.almacen_id AS id_catalogo,
                    SUM(DE.cantidad) AS cantidad_total_entrada,
                    0 AS cantidad_total_salida,
                    MAX(OE.fecha_orden) AS ultima_actualizacion
                    FROM
                    materiales_detalle_entrada AS DE
                    JOIN materiales_orden_entrada AS OE ON DE.orden_id = OE.id  
                    JOIN materiales_catalogo AS PE ON DE.almacen_id = PE.id
                    GROUP BY
                    DE.almacen_id, PE.nombre
                    UNION ALL
                    select
                    P.nombre as nombre_articulo,
                    DS.almacen_id AS id_catalogo,
                    0 AS cantidad_total_entrada,
                    SUM(DS.cantidad) AS cantidad_total_salida,
                    MAX(DOD.fecha_orden) AS ultima_actualizacion
                    FROM
                    materiales_detalle_salida AS DS
                    JOIN materiales_orden_salida AS DOD ON DS.orden_id = DOD.id
                    JOIN materiales_catalogo AS P ON DS.almacen_id = P.id
                    GROUP BY
                    DS.almacen_id, P.nombre
                ) AS subquery
                WHERE
                     ("""+ ("{} IS NULL OR {} = subquery.id_catalogo".format(producto_id, producto_id) if producto_id is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} = subquery.ultima_actualizacion".format(fecha, fecha) if fecha is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} <= subquery.ultima_actualizacion".format(fecha_inicio, fecha_inicio) if fecha_inicio is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} >= subquery.ultima_actualizacion".format(fecha_fin, fecha_fin) if fecha_fin is not None else "1=1") +""")
                GROUP BY
                nombre_articulo,
                id_catalogo
                ORDER BY
                ultima_actualizacion DESC
                 """ + ("LIMIT {}".format(cantidad_registros) if cantidad_registros is not None else "") + """
        """

        # Ejecutar la consulta SQL personalizada
        with connection.cursor() as cursor:
            cursor.execute(query)
            queryset = cursor.fetchall()
        queryset_dicts = [
            {
                'nombre_articulo': item[0],
                'id_catalogo': item[1],
                'cantidad_total_entrada': item[2],
                'cantidad_total_salida': item[3],
                'ultima_actualizacion': item[4],
                'cantidad_final': item[5],
            }
            for item in queryset
        ]
        return queryset_dicts

class SolicitudesCombinadasListCreateView(generics.ListCreateAPIView):
    serializer_class = SolicitudesSerializer

    def get_queryset(self):
        solicitud_id = self.request.query_params.get('id_solicitud', None)
        fecha = self.request.query_params.get('fecha', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        cantidad_registros = self.request.query_params.get('cantidad_registros', None)

        # Consulta SQL personalizada para obtener el resultado deseado
        query = """
            SELECT
                S.id AS id_solicitud,
                S.fecha,
                S.tipo,
                S.estado,
                S.usuario_id AS usuario,
                U.username AS nombre_usuario,
                S.descripcion,
                U.area,
                U.persona_nombre AS responsable,
                DS.id AS id_detalle_solicitud,
                DS.catalogo_id AS catalogo,
                DS.personalizado,
                DS.cantidad,
                C.nombre AS nombre_articulo,
                COALESCE(DSAL.cantidad, 0) AS cantidad_orden_salida,
                DSAL.fecha_orden AS fecha_orden_salida
            FROM
                materiales_solicitud AS S
            JOIN
                materiales_customuser AS U ON S.usuario_id = U.id
            JOIN
                materiales_detalles_solicitud AS DS ON S.id = DS.solicitud_id
            JOIN
                materiales_catalogo AS C ON DS.catalogo_id = C.id
            LEFT JOIN
                materiales_orden_salida AS OS ON S.id = OS.solicitud_id
            LEFT JOIN
                (
                    SELECT
                        DSO.orden_id,
                        DSO.almacen_id,
                        SUM(DSO.cantidad) AS cantidad,
                        MAX(OS.fecha_orden) AS fecha_orden
                    FROM
                        materiales_detalle_salida AS DSO
                    JOIN
                        materiales_orden_salida AS OS ON DSO.orden_id = OS.id
                    GROUP BY
                        DSO.orden_id,
                        DSO.almacen_id
                ) AS DSAL ON OS.id = DSAL.orden_id AND DS.catalogo_id = DSAL.almacen_id
                WHERE
                     ("""+ ("{} IS NULL OR {} = S.id_solicitud".format(solicitud_id, solicitud_id) if solicitud_id is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} = S.fecha".format(fecha, fecha) if fecha is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} <= S.fecha".format(fecha_inicio, fecha_inicio) if fecha_inicio is not None else "1=1") +""")
                AND ("""+ ("{} IS NULL OR {} >= S.fecha".format(fecha_fin, fecha_fin) if fecha_fin is not None else "1=1") +""")
                ORDER BY
                S.id DESC
                 """ + ("LIMIT {}".format(cantidad_registros) if cantidad_registros is not None else "") + """
        """

        # Ejecutar la consulta SQL personalizada
        with connection.cursor() as cursor:
            cursor.execute(query)
            queryset = cursor.fetchall()
       # Diccionario para almacenar los resultados agrupados por ID de solicitud
        queryset_dict = {}

        # Iterar sobre los resultados de la consulta y agrupar los detalles por solicitud
        for item in queryset:
            solicitud_id = item[0]
            detalle_solicitud_dict = {
                'id_Detalle_Solicitud': item[9],
                'catalogo': item[10],
                'producto_personalizado': item[11],
                'cantidad': item[12],
                'nombre_articulo': item[13],
                'cantidad_orden_salida': item[14],
                'fecha_orden_salida': item[15]
            }
            if solicitud_id not in queryset_dict:
                # Si es la primera vez que se encuentra esta solicitud, crear una nueva entrada en el diccionario
                solicitud_dict = {
                    'id_solicitud': item[0],
                    'fecha': item[1],
                    'tipo': item[2],
                    'estado': item[3],
                    'usuario': item[4],
                    'nombre_usuario': item[5],
                    'descripcion': item[6],
                    'area': item[7],
                    'responsable': item[8],
                    'detalles_solicitud': [detalle_solicitud_dict]
                }
                queryset_dict[solicitud_id] = solicitud_dict
            else:
                # Si la solicitud ya existe en el diccionario, agregar el detalle al listado existente
                queryset_dict[solicitud_id]['detalles_solicitud'].append(detalle_solicitud_dict)

        return list(queryset_dict.values())
