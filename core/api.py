from .models import *
from .serializer import *
from .mixins import *
from .filters import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password, make_password
import random
import string

#-----------------------------------------------------------------------------------------------------
# Funciones Auxiliares
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Clase para la paginación
#-----------------------------------------------------------------------------------------------------
class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pag'
    
#-----------------------------------------------------------------------------------------------------
# Función de Exception
#-----------------------------------------------------------------------------------------------------
def handle_exception(e):
    return Response({
        'data': {
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'title': ['Se produjo un error interno'],
            'errors': str(e)
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#-----------------------------------------------------------------------------------------------------
# Función para Generar Código
#-----------------------------------------------------------------------------------------------------
#-------------
def generate_verification_code(length=6, alphanumeric=False):
    if alphanumeric:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    else:
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

#-----------------------------------------------------------------------------------------------------
# Función para enviar email
#-----------------------------------------------------------------------------------------------------
def send_email(subject, template_name, context, recipient_list):
    html_content = render_to_string(template_name, context)
    send_mail(
        subject,
        '',
        'escuchamos2024@gmail.com',
        recipient_list,
        html_message=html_content,
    )
    
#-----------------------------------------------------------------------------------------------------
# Función para validar el cambio de contraseña
#-----------------------------------------------------------------------------------------------------
            
def validate_and_update_password(user, new_password):
    # Validar nueva contraseña
    if len(new_password) < 8:
        return {'validation': 'La nueva contraseña debe tener al menos 8 caracteres'}, status.HTTP_400_BAD_REQUEST

    if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
        return {'validation': 'La nueva contraseña debe ser alfanumérica'}, status.HTTP_400_BAD_REQUEST

    # Actualizar la contraseña
    user.password = make_password(new_password)
    user.save()
    
    return {'message': 'Contraseña actualizada exitosamente'}, status.HTTP_200_OK

#-----------------------------------------------------------------------------------------------------
# Autenticación
#-----------------------------------------------------------------------------------------------------   

#-----------------------------------------------------------------------------------------------------
# Iniciar Sesión
#-----------------------------------------------------------------------------------------------------   

class UserLoginAPIView(APIView):

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            username = username.lower()
            User = get_user_model()
            user = User.objects.filter(username=username, deleted_at__isnull=True).first()
            if user is not None and user.check_password(password):
                
                if user.is_active:
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    groups = user.groups.values_list('id', flat=True)  # Obtiene los nombres de los grupos del usuario
                    return Response({
                        'message': 'Inicio de sesión exitoso',
                        'token': token.key,
                        'user': user.id,
                        'groups': list(groups),  # Convertir a lista para la respuesta JSON
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Este usuario está inactivo'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'validation': 'Nombre de usuario o contraseña inválidos'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Cerrar Sesión
#-----------------------------------------------------------------------------------------------------

class UserLogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            Token.objects.filter(user=request.user).delete()
            logout(request)
            return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Registrarse
#-----------------------------------------------------------------------------------------------------
class UserRegisterAPIView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                verification_code = generate_verification_code()
                user = serializer.save(verification_code=verification_code, is_active=False)
                send_email(
                    'Verifica tu dirección de correo electrónico',
                    'verify_email.html',
                    {'username': user.username, 'verification_code': verification_code, 'user_email': user.email},
                    [user.email]
                )
                return Response({'message': 'Se ha enviado un correo electrónico de verificación'}, status=status.HTTP_200_OK)
            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Reenviar código
#-----------------------------------------------------------------------------------------------------      
class ResendVerificationCodeAPIView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get('user_email')
            if not user_email:
                return Response({'validation': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(email=user_email).first()
            
            if user and not user.is_email_verified:
                new_verification_code = generate_verification_code()
                user.verification_code = new_verification_code
                user.save()
                
                send_email(
                    'Verifica tu dirección de correo electrónico',
                    'verify_email.html',
                    {'username': user.username, 'verification_code': new_verification_code, 'user_email': user.email},
                    [user.email]
                )
                
                return Response({'message': 'Se ha enviado un nuevo correo electrónico de verificación'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Verificar codigo enviado al email
#-----------------------------------------------------------------------------------------------------
class EmailVerificationAPIView(APIView):
    def post(self, request):
        verification_code = request.data.get('verification_code')
        user_email = request.data.get('user_email')

        try:
            user = User.objects.get(email=user_email)
            if user.verification_code == verification_code:
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({'message': 'Tu dirección de correo electrónico ha sido verificada correctamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': 'El código de verificación es incorrecto'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Recuperar Cuenta
#-----------------------------------------------------------------------------------------------------
class RecoverAccountAPIView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get('user_email')
            if not user_email:
                return Response({'validation': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=user_email).first()

            if user:
                new_verification_code = generate_verification_code(length=8, alphanumeric=True)
                user.verification_code = new_verification_code
                user.save()
                
                send_email(
                    'Recupera tu cuenta',
                    'recover_account_email.html',
                    {'username': user.username, 'verification_code': new_verification_code, 'user_email': user.email},
                    [user.email]
                )
                
                return Response({'message': 'Se ha enviado un correo electrónico de recuperación de cuenta'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Verificación de recuperar la cuenta
#-----------------------------------------------------------------------------------------------------
class RecoverAccountVerificationAPIView(APIView):
    def post(self, request):
        verification_code = request.data.get('verification_code')
        user_email = request.data.get('user_email')

        try:
            user = User.objects.get(email=user_email)

            if user.verification_code == verification_code:
                if user.is_email_verified:
                    return Response({'message': 'El código ha sido verificado correctamente'}, status=status.HTTP_200_OK)
                
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({'message': 'El código ha sido verificado correctamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': 'El código de verificación es incorrecto'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Cambiar contraseña
#-----------------------------------------------------------------------------------------------------
class RecoverAccountChangePasswordAPIView(APIView):
    def put(self, request):
        user_email = request.data.get('user_email')
        new_password = request.data.get('new_password')

        if not new_password:
            return Response({'validation': 'El campo contraseña es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=user_email)
            response, status_code = validate_and_update_password(user, new_password)
            return Response(response, status=status_code)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
#-----------------------------------------------------------------------------------------------------
# Usuarios 
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Index Usuarios 
#-----------------------------------------------------------------------------------------------------
class UserIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_user'

    def get(self, request):
        try:
            users = User.objects.all()

            user_filter = UserFilter(request.query_params, queryset=users)
            filtered_users = user_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_users = pagination.paginate_queryset(filtered_users, request)
                serializer = UserSerializer(paginated_users, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = UserSerializer(filtered_users, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Actualizar Usuario 
#-----------------------------------------------------------------------------------------------------
class UserUpdateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            # Obtener el usuario autenticado
            user = request.user
            
            data = request.data.copy()
            
            # Limpiar campos vacíos
            for field in list(data.keys()):
                if data[field] in ('null', None):
                    data.pop(field)
            
            # Asegurarse de que el nombre de usuario esté en minúsculas
            if 'username' in data:
                data['username'] = data['username'].lower()
            
            serializer = UserSerializer(user, data=data, partial=True)  # Permitir actualizaciones parciales
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Usuario actualizado exitosamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Usuario 
#-----------------------------------------------------------------------------------------------------
class UserShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_user'

    def get(self, request, pk):
        try:
            user = User.objects.filter(pk=pk).first()
            if not user:
                return Response({'error': 'El ID de usuario no está registrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
            
#-----------------------------------------------------------------------------------------------------
# Cambiar Contraseña 
#-----------------------------------------------------------------------------------------------------
class UserChangePasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'validation': 'Los campos de contraseña anterior y nueva contraseña son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validar la contraseña anterior
            if not check_password(old_password, user.password):
                return Response({'validation': 'La contraseña anterior no es correcta'}, status=status.HTTP_400_BAD_REQUEST)

            response, status_code = validate_and_update_password(user, new_password)
            return Response(response, status=status_code)

        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Subir foto y borrar foto
#-----------------------------------------------------------------------------------------------------

class UserUploadPhotoAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            file_data = request.FILES.get('file')  # Nombre del campo de archivo en la solicitud
            file_type = request.data.get('type')  # Tipo de archivo en la solicitud

            if not file_data:
                return Response({'validation': 'Sube un archivo'}, status=status.HTTP_400_BAD_REQUEST)

            if file_type not in ['cover', 'profile']:
                return Response({'validation': 'El tipo de archivo es inválido. Solo se permiten "cover" o "profile"'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya existe un archivo del mismo tipo para el usuario
            existing_file = user.files.filter(type=file_type).first()

            # Almacenar el archivo usando el mixin
            file_info = self.put_file(file_data, 'photos_user', file_type=file_type)

            if existing_file:
                # Actualizar el archivo existente
                existing_file.path = file_info['path']
                existing_file.extension = file_info['extension']
                existing_file.size = file_info['size']
                existing_file.save()
                file_instance = existing_file
            else:
                # Crear un nuevo registro de archivo
                file_instance = File.objects.create(
                    content_object=user,  # Relaciona el archivo con el usuario
                    path=file_info['path'],
                    extension=file_info['extension'],
                    size=file_info['size'],
                    type=file_info['type']
                )

            # Ajusta según tu estructura de serializadores
            serializer = FileSerializer(file_instance, context={'request': request})
            return Response({'message': 'El archivo ha sido subido correctamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return handle_exception(e)
    def delete(self, request):
        try:
            user = request.user
            file_type = request.data.get('type')  # Tipo de archivo en la solicitud

            if file_type not in ['cover', 'profile']:
                return Response({'validation': 'El tipo de archivo es inválido. Solo se permiten "cover" o "profile".'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya existe un archivo del mismo tipo para el usuario
            existing_file = user.files.filter(type=file_type).first()

            if existing_file:
                # Eliminar el archivo existente del sistema de archivos
                self.delete_file(existing_file.path)

                # Eliminar el registro del archivo de la base de datos
                existing_file.delete()
                return Response({'message': 'El archivo ha sido eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'No se encontró un archivo de este tipo para el usuario'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Seguir y dejar de seguir
#-----------------------------------------------------------------------------------------------------
class FollowUserAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Obtener el usuario autenticado
            user = request.user
            
            # Obtener el ID del usuario a seguir desde los datos de la solicitud
            followed_user_id = request.data.get('followed_user_id')

            if not followed_user_id:
                return Response({'validation': 'El ID del usuario a seguir es requerido'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                followed_user = User.objects.get(id=followed_user_id)
            except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            if user.id == followed_user.id:
                return Response({'validation': 'No puedes seguirte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya sigue a este usuario
            existing_follow = Follow.objects.filter(following_user=user, followed_user=followed_user).first()

            if existing_follow:
                return Response({'error': 'Ya sigues a este usuario'}, status=status.HTTP_409_CONFLICT)

            # Crear una nueva relación de seguimiento
            follow_instance = Follow.objects.create(following_user=user, followed_user=followed_user)

            # Serializar la relación creada
            serializer = FollowSerializer(follow_instance)

            return Response({'message': 'Ahora sigues a este usuario'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return handle_exception(e)

    def delete(self, request):
        try:
            # Obtener el usuario autenticado
            user = request.user
            
            # Obtener el ID del usuario a dejar de seguir desde los datos de la solicitud
            followed_user_id = request.data.get('followed_user_id')

            if not followed_user_id:
                return Response({'validation': 'El ID del usuario a dejar de seguir es requerido'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                followed_user = User.objects.get(id=followed_user_id)
            except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            if user.id == followed_user.id:
                return Response({'validation': 'No puedes dejar de seguirte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si existe una relación de seguimiento
            follow_instance = Follow.objects.filter(following_user=user, followed_user=followed_user).first()

            if not follow_instance:
                return Response({'validation': 'No estás siguiendo a este usuario'}, status=status.HTTP_400_BAD_REQUEST)

            # Eliminar la relación de seguimiento
            follow_instance.delete()

            return Response({'message': 'Has dejado de seguir a este usuario'}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return handle_exception(e)
    def get(self, request):
            try:
                follows = Follow.objects.all()
                
                # Aplicar paginación si se requiere
                if 'pag' in request.query_params:
                    pagination = CustomPagination()
                    paginated_follows = pagination.paginate_queryset(follows, request)
                    serializer = FollowSerializer(paginated_follows, many=True, context={'request': request})
                    return pagination.get_paginated_response({'data': serializer.data})
                
                # Serializar todos los seguimientos
                serializer = FollowSerializer(follows, many=True, context={'request': request})
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                return handle_exception(e)
        
class ShowUserFollowersFollowingAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            try:
                user = User.objects.filter(pk=pk).first()
            except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            # Obtener seguidores y seguidos
            following = Follow.objects.filter(following_user=user)
            followers = Follow.objects.filter(followed_user=user)

            # Serializar los datos
            following_serializer = FollowSerializer(following, many=True, context={'request': request})
            followers_serializer = FollowSerializer(followers, many=True, context={'request': request})

            return Response({
                'data': {
                    'following': following_serializer.data,
                    'followers': followers_serializer.data,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Paises
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Index Paises
#-----------------------------------------------------------------------------------------------------
class CountryIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_country'

    def get(self, request):
        try:
            countries = Country.objects.all()

            country_filter = CountryFilter(request.query_params, queryset=countries)
            filtered_countries = country_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_countries = pagination.paginate_queryset(filtered_countries, request)
                serializer = CountrySerializer(paginated_countries, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = CountrySerializer(filtered_countries, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Paises
#-----------------------------------------------------------------------------------------------------
class CountryShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_country'

    def get(self, request, pk):
        try:
            country = Country.objects.filter(pk=pk).first()
            if not country:
                return Response({'error': 'El ID de país no está registrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CountrySerializer(country, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
            
#-----------------------------------------------------------------------------------------------------
# Estados
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Index Estados
#-----------------------------------------------------------------------------------------------------
class StatusIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_status'

    def get(self, request):
        try:
            status_p = Status.objects.all()

            status_filter = StatusFilter(request.query_params, queryset=status_p)
            filtered_status_p = status_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_status_p = pagination.paginate_queryset(filtered_status_p, request)
                serializer = StatusSerializer(paginated_status_p, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = StatusSerializer(filtered_status_p, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Estados
#-----------------------------------------------------------------------------------------------------
class StatusShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_status'

    def get(self, request, pk):
        try:
            status_p = Status.objects.filter(pk=pk).first()
            if not status_p:
                return Response({'error': 'El ID de estado no está registrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = StatusSerializer(status_p, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
            
           
#-----------------------------------------------------------------------------------------------------
# Tipos de publicación
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Index Tipos de publicación
#-----------------------------------------------------------------------------------------------------
class TypePostIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_typepost'

    def get(self, request):
        try:
            type_post = TypePost.objects.all()

            type_post_filter = TypePostFilter(request.query_params, queryset=type_post)
            filtered_type_post = type_post_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_type_post = pagination.paginate_queryset(filtered_type_post, request)
                serializer = TypePostSerializer(paginated_type_post, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = TypePostSerializer(filtered_type_post, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Tipos de publicación
#-----------------------------------------------------------------------------------------------------
class TypePostShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_typepost'

    def get(self, request, pk):
        try:
            type_post = TypePost.objects.filter(pk=pk).first()
            if not type_post:
                return Response({'error': 'El ID de tipo de publicación no está registrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TypePostSerializer(type_post, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
# Index de Reportes
#-----------------------------------------------------------------------------------------------------

class ReportAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_report'

    def get(self, request):
        try:
            report = Report.objects.all()

            report_filter = ReportFilter(request.query_params, queryset=report)
            filtered_report = report_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_report = pagination.paginate_queryset(filtered_report, request)
                serializer = ReportSerializer(paginated_report, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ReportSerializer(filtered_report, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Información de Reportes
#-----------------------------------------------------------------------------------------------------
class ReportShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_report'

    def get(self, request, pk):
        try:
            report = Report.objects.filter(pk=pk).first()
            if not report:
                return Response({'error': 'El ID del reporte no está registrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ReportSerializer(report, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

