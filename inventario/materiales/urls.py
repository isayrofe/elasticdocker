from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt
#from .backend import authenticate_with_external_jwt

urlpatterns = [
    path('proveedor/', views.ProveedorViewSet.as_view()),
    path('proveedor/<int:pk>/', views.ProveedorUpdateViewSet.as_view()),
    path('unidad/', csrf_exempt(views.UnidadViewSet.as_view())),
    path('unidad/<int:pk>/', views.UnidadUpdateViewSet.as_view()),
    path('almacen/', views.AlmacenViewSet.as_view()),
    path('almacen/<int:pk>/', views.AlmacenUpdateViewSet.as_view()),
    path('catalogo/', views.CatalogoViewSet.as_view()),
    path('catalogo/<int:pk>/', views.CatalogoUpdateViewSet.as_view()),
    path('orden_entrada/', views.OrdenEntradaListCreateView.as_view()),
    path('orden_entrada/<int:pk>/', views.OrdenEntradaUpdateView.as_view()),
    path('orden_salida/', views.OrdenSalidaListCreateView.as_view()),
    path('orden_salida/<int:pk>/', views.OrdenSalidaUpdateView.as_view()),
    path('solicitud/', views.SolicitudListCreateView.as_view()),
    path('solicitud/<int:pk>/', views.SolicitudUpdateView.as_view()),
    path('movimientos/entrada/', views.MovimientosEntradaView.as_view(), name='movimientos-entrada'),
    path('movimientos/salida/', views.MovimientosSalidaView.as_view(), name='movimientos-salida'),
    path('movimientos/', views.MovimientosView.as_view(), name='movimientos'),
    path('almacenmov/', views.MovimientosAlmacenView.as_view()),
    path('usuarios/', views.UsuariosView.as_view()),
    path('solicitudcombinada/', views.SolicitudesCombinadasListCreateView.as_view()),
    #path('vale/', views.ValeListCreateView.as_view()),
]