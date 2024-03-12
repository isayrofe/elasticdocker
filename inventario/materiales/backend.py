import requests, jwt
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from django.contrib.auth.models import User, Group
from .models import CustomUser
import re
from functools import wraps
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

grupos = {
    1: "Administradores",
    2: "Supervisores",
    3: "Operadores",
}


@api_view(['POST'])
def authenticate_with_external_jwt(request):
    
    payload = {
        "id_aplicacion": request.data.get("id_aplicacion"),
        "correo_electronico": request.data.get("correo_electronico"),
        "clave_privada": request.data.get("clave_privada"),
    }
   
    # Verificar el token con el servidor externo
    response = requests.post('http://172.80.8.188:1336/api/autenticacion', headers={'x-client-id': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibm9tYnJlIjoic2VydmljaW9zIiwiZGVzY3JpcGNpb24iOiJzaXN0ZW1hIHBhcmEgbGEgYWRtaW5pc3RyYWNpb24gZGUgdXN1YXJpb3MiLCJ1cmwiOiJodHRwczovL29hdXRoLnVpLnNlbW92aW9heGFjYS5nb2IubXgiLCJyZWRpcmVjdF91cmwiOiJodHRwczovL3dzb2F1dGguc2Vtb3Zpb2F4YWNhLmdvYi5teCIsImlhdCI6MTYxOTgwMjMyMSwiZXhwIjoxNjE5ODA3NjIxfQ.E96yPDbol1UWdyXVXsCla3leVSs1ZdYy9b5J2JL0TZPZn5-b60jgSvVmWXxXAfAM5nduN_dZo78cxYbaQ5zHCT8fuAGAGUqPDxieAArShZwVIbK1GymHR4P14vcBK-kdJLGWMuxCpg2F5IfWKlkChF6n_YuwrUv5wHjSberGA81mI3AdwbYO1CxZGnHwS6GhyYSY10dyVVk6ZqDg_GNdSgnGNMO2l2EoUYvsg0BFJN8gGBRm9I6fZ-cxVi6g6v8-9oZSqL9QYyOhlzotFZ8pXn1rmlWhHEI8z-f0Xv_Ekh2w3gkXTydE6pbozQ8As50CRQerfnsW_PActYUHDbN-Ow'},json=payload)

    token = response.json().get('X_TOKEN_ACCOUNT')
    #token = request.data.get('X_TOKEN_ACCOUNT')  # Supongamos que el token se pasa en el cuerpo de la solicitud POST
    if token is not None:
        # Verificar el token con el servidor externo
        response = requests.post('http://172.80.8.188:1336/api/autenticacion/perfil', headers={'Authorization': f'Bearer {token}'})
        #return Response(response.json())
        if len(response.json()) > 0:
        #if response.status_code == 200:
            user_data = response.json()

            # Decodificar el token para obtener más información (si es necesario)
            # Si el usuario existe, loguearlo
            usuario = re.match(r'([^@]+)@', user_data['usuario']).group(1)
            try:
                user = CustomUser.objects.get(username=usuario)
                login(request, user)
                return Response({'message': 'Autenticación exitosa'})
            except CustomUser.DoesNotExist:
                # Si el usuario no existe, crearlo
                response_area = requests.post('http://172.80.8.188:1336/api/area/{}'.format(user_data['area']), headers={'Authorization': f'Bearer {token}'})
                data = {
                         'username': usuario,
                         'first_name': user_data['persona_nombre'],
                         'email': user_data['usuario'],
                         'password': "isayrobles"
                        }
                try:
                    rol = user_data['rol']
                    user = CustomUser.objects.create_user(**data)
                    login(request, user)
                    user_data = response.json()
                    #user_id = user_data['id']
                    # Asignar el usuario a un grupo
                    try:
                        group = Group.objects.get(name=grupos[rol])
                        #user = User.objects.get(id=user_id)
                        user.groups.add(group)
                        user.save()
                    except Group.DoesNotExist:
                        print('El grupo no existe')
                        pass
                    return Response({'message': 'Autenticación exitosa'})
                except Exception as e:
                    print('Error al crear el usuario:', e)
                    pass

    # Si el token es inválido, devolver un error de autenticación
    return Response({'message': 'Error de autenticación'}, status=401)


#@method_decorator(csrf_exempt, name='dispatch')
def external_token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtener el token externo de la solicitud (supongamos que está en el encabezado)
        external_token = request.headers.get('Authorization')  # Ajusta esto según cómo recibes el token
        external_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoiYWRtaW5pc3RyYWRvckBzZW1vdmlvYXhhY2EuZ29iLm14IiwidXN1YXJpb19pZCI6IjEiLCJyb2wiOjEsImFwbGljYWNpb24iOjEsImFyZWEiOiIxIiwibW9kdWxvIjoiNSIsIm1vZHVsb19ub21icmUiOiJNw5NEVUxPIENBUkxPUyBHUkFDSURBIiwicGVyc29uYSI6IjEiLCJwZXJzb25hX25vbWJyZSI6IkFETUlOSVNUUkFET1IgREVMIFNJU1RFTUEiLCJub21icmVfYXBsaWNhY2lvbiI6InNlcnZpY2lvcyIsImlhdCI6MTcwOTIwMjg2NSwiZXhwIjoxNzA5MjIwODY1fQ.KXRN-8Tv78HO2d4ZHftsk8w_b3Q6yjwE8VnVRGT7BK86VTKXK77Oth32XD_mTd9GAFVXduCGs_AbNfnFPcezg5dVqqWUB4x8Y2lO2VstLPuSxxb0doW5NsWfQBDo2LPSnkys1v4S4MaHWDcJVdpjoaXjsCSr-OZWxxvBzuOdNw66eNpO3YLPtqLBvWedC-4gXQ5Hpk7MCnOrhV-St6boYQ5k6ypo_E2xlz8lW8w5PRWSdzvcrsD-M0axC_N5DjfWBU5q3yhVZiwc4PmJdswW06MNC5IGPDDceVaeeCmzBp1IdFn4Finahz_StV-c1e0fpRKHhgMAJ7h9eLyRAv0AFA"
        response = requests.post('http://172.80.8.188:1336/api/usuario/perfil', headers={'Authorization': f'{external_token}'})
        # Verificar el token externo (aquí deberías implementar tu lógica de validación)
        if (response.status_code == 200) and (response.json() is not None):  # Implementa esta función de validación
            user_data = response.json()

            # Si el usuario existe, loguearlo
            usuario = re.match(r'([^@]+)@', user_data['usuario']['correo_electronico']).group(1)
            try:
                user = CustomUser.objects.get(username=usuario)
                #response.headers.pop('Authorization', None)
                # Verificar si el usuario está activo
                
                # if request.user.is_authenticated and request.user.username == user.username:
                #    return view_func(request, *args, **kwargs)
                # Loguear al usuario
                login(request, user)
                return view_func(request, *args, **kwargs)
            except CustomUser.DoesNotExist:
                # Si el usuario no existe, crearlo
                # areas = 'http://172.80.8.188:1336/api/usuario/perfil'.format(user_data['area'])
                # response_area = requests.get(areas, headers={'Authorization': f'{external_token}'})
                # general_data = response_area.json()
                # areas = 'http://172.80.8.188:1336/api/usuario/perfil'.format(user_data['area'])
                # response_area = requests.get(areas, headers={'Authorization': f'{external_token}'})
                # area_data = response_area.json()
                data = {
                         'username': usuario,
                         'persona_nombre': user_data['persona']['nombre']+" "+user_data['persona']['primer_apellido']+" "+user_data['persona']['segundo_apellido'],
                         'first_name': user_data['persona']['nombre'],
                         'last_name': user_data['persona']['primer_apellido']+" "+user_data['persona']['segundo_apellido'],
                         'email': user_data['usuario']['correo_electronico'],
                         'password': "1.2.3.4.5",
                         'modulo':user_data['modulo']['nombre'],
                         'area':user_data['area']['nombre']
                        }
                try:
                    rol = user_data['rol']['id']
                    user = CustomUser.objects.create_user(**data)
                    login(request, user)
                    user_data = response.json()
                    #user_id = user_data['id']
                    # Asignar el usuario a un grupo
                    try:
                        group = Group.objects.get(name=grupos[rol])
                        #user = User.objects.get(id=user_id)
                        user.groups.add(group)
                        user.save()
                    except Group.DoesNotExist:
                        print('El grupo no existe')
                        pass
                    #return Response({'message': 'Autenticación exitosa'})
                    return view_func(request, *args, **kwargs)
                except Exception as e:
                    print('Error al crear el usuario:', e)
                    pass
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('Acceso no autorizado')  # Cambia el mensaje de error según sea necesario
    return wrapper
