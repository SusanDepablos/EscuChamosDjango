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
from django.contrib.sessions.models import Session
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from core.models import HistoricalUser
from django.utils import timezone
from datetime import timedelta
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
            'title': ['Se produjo un error interno.'],
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
    # Validar que la nueva contraseña no sea la misma que la anterior
    if check_password(new_password, user.password):
        return {'validation': {'new_password': ['La nueva contraseña no puede ser igual a la anterior.']}}, status.HTTP_400_BAD_REQUEST

    # Validación de longitud y contenido de la contraseña
    if len(new_password) < 8:
        return {'validation': {'new_password': ['La contraseña debe tener al menos 8 caracteres.']}}, status.HTTP_400_BAD_REQUEST
    if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
        return {'validation': {'new_password': ['La contraseña debe ser alfanumérica.']}}, status.HTTP_400_BAD_REQUEST

    # Actualizar la contraseña
    user.set_password(new_password)
    user.save()
    return {'message': 'Contraseña actualizada exitosamente.'}, status.HTTP_200_OK


#-----------------------------------------------------------------------------------------------------
# Función para cambiar estado de un modelo
#-----------------------------------------------------------------------------------------------------

def update_object_status(content_type_id, object_id, status_id):
    try:
        # Obtener el modelo del objeto a partir del content_type
        content_type = ContentType.objects.get(id=content_type_id)
        model_class = content_type.model_class()
        
        # Obtener el objeto a partir del object_id
        obj = model_class.objects.get(id=object_id)
        
        if hasattr(obj, 'status'):
            # Obtener el nuevo estado
            new_status = Status.objects.get(id=status_id)

            obj.status = new_status  # Actualiza el estado del objeto
            obj.save()
            
            if new_status.name.lower() in ['resuelto', 'bloqueado']:
                # Eliminar todos los reportes asociados al objeto
                obj.reports.all().delete()

            # Lógica especial si el estado es "bloqueado"
            if new_status.name.lower() == 'bloqueado':
                handle_blocked_status(obj)
                
            return Response({'message': 'Reporte creado exitosamente.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'El objeto no tiene un campo de estado.'}, status=status.HTTP_404_NOT_FOUND)

    except Status.DoesNotExist:
        return Response({'error': 'Estatus no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

#-----------------------------------------------------------------------------------------------------
# Función para manejar el estado bloqueado de un post o comment
#-----------------------------------------------------------------------------------------------------
def handle_blocked_status(obj): 
    if isinstance(obj, Post):
        # Si el objeto es un post, bloquea todos los reposts de ese post
        reposts = Post.objects.filter(post=obj)  # Filtra todos los reposts del post original
        
        reposts.update(status=Status.objects.get(name__iexact='bloqueado'))  # Cambia el estado a "bloqueado"

        shares = Share.objects.filter(post=obj)  # Filtra todos los shares del post
        
        shares.delete()  # Elimina todos los share

    # Agrega cualquier otra lógica que necesites aquí
    print('Estado bloqueado manejado correctamente.')

#-----------------------------------------------------------------------------------------------------
# Autenticación
#-----------------------------------------------------------------------------------------------------   

#-----------------------------------------------------------------------------------------------------
# Groups
#-----------------------------------------------------------------------------------------------------   

class GroupIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_group'

    def get(self, request):
        try:
            groups = Group.objects.all()

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_posts = pagination.paginate_queryset(groups, request)
                serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
                # El método `get_paginated_response` ya retorna un Response
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = GroupSerializer(groups, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Iniciar Sesión
#-----------------------------------------------------------------------------------------------------   

class UserLoginAPIView(APIView):

    def post(self, request):
        # Obtener los datos del request
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        
        # Inicializar un diccionario para almacenar los errores
        errors = {}

        # Validar el campo de nombre de usuario
        if not username:
            errors['username'] = ['Este campo no puede estar en blanco.']
        
        # Validar el campo de contraseña
        if not password:
            errors['password'] = ['Este campo no puede estar en blanco.']

        # Si hay errores, devolverlos en la respuesta
        if errors:
            return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

        # Si no hay errores, proceder con la lógica de autenticación
        try:
            username = username.lower()
            User = get_user_model()
            user = User.objects.filter(username=username, deleted_at__isnull=True).first()
            if user is not None and user.check_password(password):
                
                if user.is_active:
                    # Iniciar sesión del usuario
                    login(request, user)
                    
                    # Obtener o crear el token
                    token, created = Token.objects.get_or_create(user=user)
                    
                    # Obtener la clave de la sesión actual
                    session_key = request.session.session_key
                    
                    # Crear o actualizar el registro en SessionInfo
                    session_info, created = SessionInfo.objects.update_or_create(
                        user=user,
                        session_key=session_key,
                        token_key=token.key,
                        defaults={'device_info': request.META.get('HTTP_USER_AGENT', '')}  # Guarda la información del dispositivo
                    )
                    
                    # Obtener los grupos del usuario
                    groups = user.groups.values_list('id', flat=True)  # Obtiene los nombres de los grupos del usuario
                    
                    # Devolver una respuesta exitosa con la información de sesión y token
                    return Response({
                        'message': 'Inicio de sesión exitoso.',
                        'token': token.key,
                        'session_key': session_key,
                        'user': user.id,
                        'groups': list(groups),  # Convertir a lista para la respuesta JSON
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Este usuario está inactivo.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'validation': 'Nombre de usuario o contraseña inválidos.'}, status=status.HTTP_400_BAD_REQUEST)
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
            session_key = request.data.get('session_key')
            
            if not session_key:
                return Response({'validation': 'Tienes que enviar el session_key.'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = Token.objects.get(user=request.user)

            session_info_count = SessionInfo.objects.filter(token_key=token.key).count()
            
            SessionInfo.objects.filter(session_key=session_key).delete()

            Session.objects.filter(session_key=session_key).delete()

            if session_info_count == 1:
                token.delete()

            if session_key == request.session.session_key:
                logout(request)
            
            return Response({'message': 'Sesión cerrada exitosamente.'}, status=status.HTTP_200_OK)
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
                return Response({'message': 'Se ha enviado un correo electrónico de verificación.'}, status=status.HTTP_200_OK)
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
                return Response({'validation': 'El campo email es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
            
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
                
                return Response({'message': 'Se ha enviado un nuevo correo electrónico de verificación.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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
                return Response({'message': 'Tu dirección de correo electrónico ha sido verificada correctamente.'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': 'El código de verificación es incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
                return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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
                return Response({'validation': 'El campo email es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

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
                
                return Response({'message': 'Se ha enviado un correo electrónico de recuperación de cuenta.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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
                    return Response({'message': 'El código ha sido verificado correctamente.'}, status=status.HTTP_200_OK)
                
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({'message': 'El código ha sido verificado correctamente.'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': 'El código de verificación es incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Cambiar contraseña
#-----------------------------------------------------------------------------------------------------
class RecoverAccountChangePasswordAPIView(APIView):
    def put(self, request):
        user_email = request.data.get('user_email')
        new_password = request.data.get('new_password')
        # Diccionario para almacenar los errores
        errors = {}

        # Validar el campo de nueva contraseña
        if not new_password:
            errors['new_password'] = ['La nueva contraseña es requerida.']

        # Si hay errores, devolverlos en la respuesta
        if errors:
            return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=user_email)
            response, status_code = validate_and_update_password(user, new_password)
            return Response(response, status=status_code)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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

    def get(self, request):
        try:
            time_threshold = timezone.now() - timedelta(hours=24)

            User.objects.filter(created_at__lt=time_threshold, is_email_verified=False).delete()

            # Obtiene todos los usuarios excepto el usuario autenticado y que estén activos
            users = User.objects.exclude(id=request.user.id).filter(is_active=True)

            user_filter = UserFilter(request.query_params, queryset=users)
            filtered_users = user_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_users = pagination.paginate_queryset(filtered_users, request)
                serializer = UserSerializer(paginated_users, many=True, context={'request': request})
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
            
            # Validar que el correo sea de @gmail.com si se está actualizando el email
            if 'email' in data:
                email = data['email']
                if not email.endswith('@gmail.com'):
                    return Response(
                        {'validation': {
                            'email': [
                                'El correo debe ser una dirección de @gmail.com.'
                            ]
                        }},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Crear el serializer y permitir actualizaciones parciales
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Usuario actualizado exitosamente.'}, status=status.HTTP_200_OK)
            else:
                return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return handle_exception(e)

        
#-----------------------------------------------------------------------------------------------------
# Actualizar Usuario 
#-----------------------------------------------------------------------------------------------------
class  UserVerifyPasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            password = request.data.get('password')

            error = {}

            if not password:
                error['password'] = ['Este campo no puede estar en blanco.']

            if error:
                return Response({'validation': error}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                return Response({'message': 'La contraseña es correcta.'}, status=status.HTTP_200_OK)

            else:
                return Response({'validation': 'La contraseña es incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({'error': 'El ID de usuario no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
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

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        errors = {}

        # Validación para old_password
        if not old_password:
            errors['old_password'] = ['Este campo no puede estar en blanco.']

        # Validación para new_password
        if not new_password:
            errors['new_password'] = ['Este campo no puede estar en blanco.']
        else:
            # Aplicar la validación personalizada de la nueva contraseña
            try:
                self.validate_password(new_password)
            except serializers.ValidationError as e:
                errors['new_password'] = [str(msg) for msg in e.detail]

        # Validación adicional para comprobar que la nueva contraseña no sea igual a la anterior
        if new_password == old_password:
            errors['new_password'] = ['La nueva contraseña no puede ser igual a la anterior.']

        # Si hay errores, se devuelven
        if errors:
            return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validar la contraseña actual
            if not check_password(old_password, user.password):
                return Response({'validation': {'old_password': ['La contraseña actual no es correcta.']}}, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar la contraseña
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)

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
                return Response({'validation': 'Sube un archivo.'}, status=status.HTTP_400_BAD_REQUEST)

            if file_type not in ['cover', 'profile']:
                return Response({'validation': 'El tipo de archivo es inválido. Solo se permiten "cover" o "profile".'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'message': 'La foto se ha subido exitosamente.'}, status=status.HTTP_201_CREATED)

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
                return Response({'message': 'La foto ha sido eliminada correctamente.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'No se encontró la foto.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Editar y eliminar Usuarios con el admin
#-----------------------------------------------------------------------------------------------------

class UserGroupUpdateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        errors = {}
        try:
            # Obtener el usuario por id
            user = User.objects.get(id=user_id)

            # Verificar si el usuario existe y el solicitante tiene permiso
            if not user:
                return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            # Obtener el grupo enviado en los datos de la solicitud
            group_id = request.data.get('group_id')
            
            if not group_id:
                errors['group_id'] = ['Tiene que elegir un rol.']

            # Si hay errores de validación, devolverlos
            if errors:
                return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si el grupo existe
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                return Response({'error': 'Rol no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            # Actualizar el grupo del usuario
            user.groups.clear()  # Limpiar los grupos actuales
            user.groups.add(group)  # Agregar el nuevo grupo

            return Response({'message': 'Usuario actualizado exitosamente.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def delete(self, request, user_id):
        try:
            # Obtener el usuario por id
            user = User.objects.get(id=user_id)

            # Eliminar el usuario
            user.delete()

            return Response({'message': 'Usuario eliminado exitosamente.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Seguimientos
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
# Seguir y dejar de seguir
#-----------------------------------------------------------------------------------------------------
class FollowUserIndexCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            follows = Follow.objects.all()
            
            follow_filter = FollowFilter(request.query_params, queryset=follows)
            filtered_follows = follow_filter.qs
            
            # Verificar si se ha pasado un id para mostrar primero
            highlight_id = request.query_params.get('highlight_id')  # ID a resaltar
            if highlight_id:
                try:
                    specific_follow = filtered_follows.get(id=highlight_id)
                    filtered_follows = filtered_follows.exclude(id=highlight_id)  # Excluirlo de la lista
                    # Agregar el seguimiento específico al principio
                    filtered_follows = [specific_follow] + list(filtered_follows)
                except Follow.DoesNotExist:
                    pass  # Si no existe, simplemente ignorar
            
            # Aplicar paginación si se requiere
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_follows = pagination.paginate_queryset(filtered_follows, request)
                serializer = FollowSerializer(paginated_follows, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            # Serializar todos los seguimientos
            serializer = FollowSerializer(filtered_follows, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

    def post(self, request):
        try:
            # Obtener el usuario autenticado
            user = request.user
            
            # Obtener el ID del usuario a seguir desde los datos de la solicitud
            followed_user_id = request.data.get('followed_user_id')

            if not followed_user_id:
                return Response({'validation': 'El ID del usuario a seguir es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener el usuario a seguir
            followed_user = User.objects.get(id=followed_user_id)

            if user.id == followed_user.id:
                return Response({'validation': 'No puedes seguirte a ti mismo.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya sigue a este usuario
            existing_follow = Follow.objects.filter(following_user=user, followed_user=followed_user).first()

            if existing_follow:
                # Si ya existe, eliminar la relación de seguimiento
                existing_follow.delete()
                return Response({'message': 'Has dejado de seguir a este usuario.'}, status=status.HTTP_200_OK)
            else:
                # Si no existe, crear una nueva relación de seguimiento
                Follow.objects.create(following_user=user, followed_user=followed_user)
                return Response({'message': 'Ahora sigues a este usuario.'}, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
class FollowUserDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # Obtener el usuario usando el pk en la URL
            user = User.objects.get(pk=pk)
            
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
        
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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
                serializer = CountrySerializer(paginated_countries, many=True, context={'request': request})
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
            # Obtener el país usando el pk
            country = Country.objects.get(pk=pk)

            # Serializar los datos del país
            serializer = CountrySerializer(country, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Country.DoesNotExist:
            return Response({'error': 'El ID de país no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
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
            statuses = Status.objects.all()

            status_filter = StatusFilter(request.query_params, queryset=statuses)
            filtered_statuses = status_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_statuses = pagination.paginate_queryset(filtered_statuses, request)
                serializer = StatusSerializer(paginated_statuses, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = StatusSerializer(filtered_statuses, many=True, context={'request': request})
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
            # Obtener el estado usando el pk
            status_p = Status.objects.get(pk=pk)

            # Serializar los datos del estado
            serializer = StatusSerializer(status_p, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Status.DoesNotExist:
            return Response({'error': 'El ID de estado no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
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
            type_posts = TypePost.objects.all()

            type_post_filter = TypePostFilter(request.query_params, queryset=type_posts)
            filtered_type_posts = type_post_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_type_posts = pagination.paginate_queryset(filtered_type_posts, request)
                serializer = TypePostSerializer(paginated_type_posts, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = TypePostSerializer(filtered_type_posts, many=True, context={'request': request})
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
            # Obtener el tipo de publicación usando el pk
            type_post = TypePost.objects.get(pk=pk)

            # Serializar los datos del tipo de publicación
            serializer = TypePostSerializer(type_post, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except TypePost.DoesNotExist:
            return Response({'error': 'El ID de tipo de publicación no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Reacciones
#-----------------------------------------------------------------------------------------------------
class ReactionIndexCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_reaction'

    def get(self, request):
        try:
            reactions = Reaction.objects.all()

            reaction_filter = ReactionFilter(request.query_params, queryset=reactions)
            filtered_reactions = reaction_filter.qs
            
            # Verificar si se ha pasado un id para mostrar primero
            highlight_id = request.query_params.get('highlight_id')  # ID a resaltar
            if highlight_id:
                try:
                    specific_reaction = filtered_reactions.get(id=highlight_id)
                    filtered_reactions = filtered_reactions.exclude(id=highlight_id)  # Excluirlo de la lista
                    # Agregar la reacción específica al principio
                    filtered_reactions = [specific_reaction] + list(filtered_reactions)
                except Reaction.DoesNotExist:
                    pass  # Si no existe, simplemente ignorar
                
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_reactions = pagination.paginate_queryset(filtered_reactions, request)
                serializer = ReactionSerializer(paginated_reactions, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ReactionSerializer(filtered_reactions, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
    def post(self, request):
        user = request.user
        data = request.data.copy()  # Copia los datos del request para agregar el usuario
        data['user'] = user.id  # Agrega el ID del usuario al diccionario de datos

        # Obtener el nombre del modelo desde los datos enviados
        model_name = data.get('model')  # Ejemplo: 'post'
        object_id = data.get('object_id')  # ID del objeto relacionado

        try:
            blocked_id = Status.objects.get(name='Bloqueado').id
            # Verificar que el modelo exista en ContentType
            content_type = ContentType.objects.get(model=model_name.lower())

            # Verificar que el objeto relacionado exista
            model_class = content_type.model_class()
            obj = model_class.objects.get(id=object_id)

        
            if obj.status_id == blocked_id:
                return Response(status=status.HTTP_204_NO_CONTENT)

            # Agregar el content_type_id al diccionario de datos
            data['content_type'] = content_type.id

            # Verificar si la reacción ya existe para el mismo usuario, content_type y objeto
            existing_reaction = Reaction.objects.filter(
                user=user,
                content_type=content_type,
                object_id=object_id
            ).first()

            if existing_reaction:
                # Si la reacción ya existe, eliminarla
                existing_reaction.delete()
                return Response({'message': 'Reacción eliminada exitosamente.'}, status=status.HTTP_200_OK)
            else:
                # Si no existe, crear una nueva reacción
                serializer = ReactionSerializer(data=data)
                if serializer.is_valid():
                    reaction = serializer.save()
                    return Response({'message': 'Reacción creada exitosamente.'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except ContentType.DoesNotExist:
            return Response({'error': 'Modelo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except model_class.DoesNotExist:
            return Response({'error': 'El objeto relacionado no se encontró.'}, status=status.HTTP_404_NOT_FOUND)
        # Manejo de excepciones generales
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Información de Reacciones
#-----------------------------------------------------------------------------------------------------
class ReactionDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_reaction'

    def get(self, request, pk):
        try:
            # Obtener la reacción usando el pk
            reaction = Reaction.objects.get(pk=pk)

            # Serializar los datos del reactione
            serializer = ReactionSerializer(reaction, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Reaction.DoesNotExist:
            return Response({'error': 'El ID del reacción no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------

class ReportIndexGroupedPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Obtener el estado "Reportado"
            reported_status = Status.objects.get(name__iexact='reportado')

            # Obtener los IDs de los comentarios que están en estado "Reportado"
            reported_comments_ids = Comment.objects.filter(status=reported_status).values_list('id', flat=True)

            # Obtener los IDs de las publicaciones que están en estado "Reportado"
            reported_posts_ids = Post.objects.filter(status=reported_status).values_list('id', flat=True)

            # Combinar los IDs de comentarios y publicaciones
            combined_ids = list(reported_comments_ids) + list(reported_posts_ids)

            # Obtener el tipo de objeto desde los parámetros de la consulta (opcional)
            object_type = request.query_params.get('type', None)

            # Filtrar los reportes, agrupándolos por content_type y object_id, y contando los reportes
            reports = Report.objects.filter(object_id__in=combined_ids)
            
            report_filter = ReportGroupedFilter(request.query_params, queryset=reports)
            reports = report_filter.qs  # Obtiene el queryset filtrado

            # Agrupar y contar reportes
            reports = (
                reports
                .values('content_type', 'object_id')
                .annotate(reports_count=Count('id'))  # Cuenta los reportes para cada combinación
                .order_by('-reports_count')  # Ordena por el conteo de reportes de forma descendente
            )

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_reports = pagination.paginate_queryset(reports, request)
                serializer = ReportGroupedSerializer(paginated_reports, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})

            # Serializar los reportes
            serializer = ReportGroupedSerializer(reports, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

        
class ReportIndexCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_report'

    def get(self, request):
        try:
            reports = Report.objects.all().order_by('-created_at')

            report_filter = ReportFilter(request.query_params, queryset=reports)
            filtered_reports = report_filter.qs

            
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_reports = pagination.paginate_queryset(filtered_reports, request)
                serializer = ReportSerializer(paginated_reports, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ReportSerializer(filtered_reports, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
    def post(self, request):
        user = request.user
        data = request.data.copy()  # Copia los datos del request para agregar el usuario
        data['user'] = user.id  # Agrega el ID del usuario al diccionario de datos

        model_name = data.get('model')  # Ejemplo: 'post'
        object_id = data.get('object_id')  # ID del objeto relacionado
        observation = data.get('observation')  # Observación del reporte

        try:
            # Verificar que el modelo exista en ContentType
            content_type = ContentType.objects.get(model=model_name.lower())

            # Verificar que el objeto relacionado exista
            model_class = content_type.model_class()
            obj = model_class.objects.get(id=object_id)

            # Agregar el content_type_id al diccionario de datos
            data['content_type'] = content_type.id

            # Serializar y guardar el reporte
            serializer = ReportSerializer(data=data)
            if serializer.is_valid():
                report = serializer.save()  # Guarda el reporte

                try:
                    # Buscar el ID del estado cuyo nombre es 'Reportado'
                    reported_status = Status.objects.get(name__iexact='reportado')
                    
                    # Llamar a la función con el ID del estado 'Reportado'
                    response = update_object_status(
                        report.content_type.id, 
                        report.object_id, 
                        reported_status.id  # Asigna el ID dinámicamente
                    )
                except ObjectDoesNotExist:
                    # Manejar el caso en que no exista un estado llamado 'Reportado'
                    return Response({'error': 'Estado "Reportado" no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
                
                return response  # Retorna la respuesta de la función
            else:
                return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except ContentType.DoesNotExist:
            return Response({'error': 'Modelo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except model_class.DoesNotExist:
            return Response({'error': 'El objeto relacionado no se encontró.'}, status=status.HTTP_404_NOT_FOUND)

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
            # Obtener el reporte usando el pk
            report = Report.objects.get(pk=pk)

            # Serializar los datos del reporte
            serializer = ReportSerializer(report, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Report.DoesNotExist:
            return Response({'error': 'El ID del reporte no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
class UpdateStatusAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        model = data.get('model')  # Ejemplo: 'post'
        object_id = data.get('object_id')  # ID del objeto relacionado
        status_id = data.get('status_id')  # ID del nuevo estado

        try:
            # Verificar que el modelo exista en ContentType
            content_type = ContentType.objects.get(model=model.lower())

            # Llamar a la función para actualizar el estado del objeto
            response = update_object_status(content_type.id, object_id, status_id)
            return response

        except ContentType.DoesNotExist:
            return Response({'error': 'Modelo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Publicaciones
#-----------------------------------------------------------------------------------------------------
class PostIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_post'

    def get(self, request):
        try:
            posts = Post.objects.exclude(status__name__iexact='bloqueado').order_by('-created_at')

            post_filter = PostFilter(request.query_params, queryset=posts)
            filtered_posts = post_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_posts = pagination.paginate_queryset(filtered_posts, request)
                serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
                # El método `get_paginated_response` ya retorna un Response
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = PostSerializer(filtered_posts, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            blocked_id = Status.objects.get(name='Bloqueado').id
            # Obtener el post_id de la publicación padre desde request.data
            post_id = request.data.get('post_id')
            
            if post_id and not Post.objects.filter(pk=post_id).exists():
                return Response(
                    {'error': 'El ID de la publicación no está registrado.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if post_id:
                post = Post.objects.get(id=post_id)
                if post.status_id == blocked_id:
                    return Response(status=status.HTTP_204_NO_CONTENT)

            # Separar archivos y otros datos
            file_list = request.FILES.getlist('file')  # Obtiene la lista de archivos, si existen
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            # Asignar datos adicionales al diccionario
            try:
                # Buscar el ID del estado cuyo nombre es 'Activo'
                active_status = Status.objects.get(name__iexact='activo')

                other_data['status_id'] = active_status.id
            except ObjectDoesNotExist:
                # Manejar el caso en que no exista un estado llamado 'Activo'
                return Response({'error': 'Estado "Activo" no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Asignar el ID del usuario
            other_data['user_id'] = request.user.id
            
            # Crear una instancia del serializer con los datos restantes
            serializer = PostSerializer(data=other_data)

            if serializer.is_valid():
                type_post_id = int(request.data.get('type_post_id')[0])
                errors = {}

                if type_post_id == 2 and not file_list:
                    errors['file'] = ['Este campo no puede estar en blanco.']

                if type_post_id == 1 and not request.data.get('body'):
                    errors['body'] = ['Este campo no puede estar en blanco.']
                    
                if type_post_id == 4:
                    # Si no hay archivos, el cuerpo es obligatorio
                    if not file_list and not request.data.get('body'):
                        errors['body'] = ['Este campo no puede estar en blanco.']

                if errors:
                    return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

                # Guardar la publicación asegurando que se pase post_id
                post_instance = serializer.save(post_id=post_id)

                if file_list:
                    for index, file_data in enumerate(file_list):
                        file_type = str(index + 1)  # Asignar el tipo de archivo según el índice

                        # Lógica para guardar el archivo usando FileUploadMixin
                        file_info = self.put_file(file_data, 'posts', file_type=file_type)

                        # Crear instancia de File asociada a la publicación
                        File.objects.create(
                            content_object=post_instance,  # Relaciona el archivo con la publicación
                            path=file_info['path'],
                            extension=file_info['extension'],
                            size=file_info['size'],
                            type=file_info['type']
                        )
                    
                return Response({'message': 'Publicación creada exitosamente.'}, status=status.HTTP_201_CREATED)

            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejo de excepciones
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Publicaciones
#-----------------------------------------------------------------------------------------------------
class PostDetailAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_post'

    def get(self, request, pk):
        try:
            # Obtener la publicación usando el pk
            post = Post.objects.get(pk=pk)

            # Serializar los datos de la publicación
            serializer = PostSerializer(post, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({'error': 'El ID de publicación no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
    def put(self, request, pk):
        try:
            # Obtener la publicación usando el pk
            post = Post.objects.get(pk=pk)

            # Obtener el nuevo valor para `body` y el tipo de publicación
            new_body = request.data.get('body')
            type_post_id = post.type_post_id

            # Validar que el campo `body` sea proporcionado si el tipo de publicación es 1
            if type_post_id == 1 and not new_body:
                return Response({'validation': {'body': ['Este campo no puede estar en blanco.']}}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar el campo `body` si se proporciona un nuevo valor
            if new_body is not None:
                post.body = new_body

            # Guardar los cambios en la publicación
            post.save()

            # Serializar los datos actualizados de la publicación
            serializer = PostSerializer(post, context={'request': request})

            return Response({'message': 'Publicación actualizada exitosamente.'}, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({'error': 'El ID de publicación no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def delete(self, request, pk):
        try:
            # Obtener la publicación usando el pk
            post = Post.objects.get(pk=pk)
            type_post_id = post.type_post_id

            # Eliminar archivos asociados si el tipo de publicación es 2
            if type_post_id == 2:
                files = post.files.all()  # Obtener todos los archivos asociados a la publicación
                for file in files:
                    self.delete_file(file.path)  # Eliminar el archivo del sistema
                    file.delete()  # Eliminar el registro del archivo de la base de datos

            # Eliminar la publicación
            post.delete()

            return Response({'message': 'La publicación ha sido eliminada correctamente.'}, status=status.HTTP_202_ACCEPTED)

        except Post.DoesNotExist:
            return Response({'error': 'El ID de publicación no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Compartir
#-----------------------------------------------------------------------------------------------------
class ShareIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_share'

    def get(self, request):
        try:
            shares = Share.objects.all().order_by('-created_at')
            
            share_filter = ShareFilter(request.query_params, queryset=shares)
            filtered_shares = share_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_shares = pagination.paginate_queryset(filtered_shares, request)
                serializer = ShareSerializer(paginated_shares, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ShareSerializer(filtered_shares, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            blocked_id = Status.objects.get(name='Bloqueado').id

            data = request.data.copy()
            data['user_id'] = request.user.id
            post_id = request.data.get('post_id')

            if post_id:
                post = Post.objects.get(id=post_id)
                if post.status_id == blocked_id:
                    return Response(status=status.HTTP_204_NO_CONTENT)

            # Serializar los datos de entrada
            serializer = ShareSerializer(data=data, context={'request': request})
            
            # Validar y guardar el nuevo share
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'El compartido se ha creado exitosamente.'}, status=status.HTTP_201_CREATED)
            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejo de excepciones
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Publicaciones
#-----------------------------------------------------------------------------------------------------
class ShareDetailAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_share'

    def get(self, request, pk):
        try:
            # Obtener la compartido usando el pk
            share = Share.objects.get(pk=pk)

            # Serializar los datos de la compartido
            serializer = ShareSerializer(share, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Share.DoesNotExist:
            return Response({'error': 'El ID de compartido no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def delete(self, request, pk):
        try:
            # Obtener el share usando el pk
            share = Share.objects.get(pk=pk)

            # Verificar si el usuario autenticado es el propietario del share
            if share.user != request.user:
                return Response({'error': 'No tienes permiso para eliminar este compartido.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Eliminar el share
            share.delete()
            return Response({'message': 'El compartido ha sido eliminado exitosamente.'}, status=status.HTTP_202_ACCEPTED)

        except Share.DoesNotExist:
            return Response({'error': 'El ID de compartido no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)

#-----------------------------------------------------------------------------------------------------
# Comentarios
#-----------------------------------------------------------------------------------------------------
class CommentIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_comment'

    def get(self, request):
        try:
            comments = Comment.objects.exclude(
                status__name__iexact='bloqueado'  # Excluir comentarios de publicaciones bloqueadas
            ).annotate(
                reactions_count=Count('reactions')
            ).order_by('-reactions_count', '-created_at')  # Ordenar por reacciones y luego por fecha de creación

            comment_filter = CommentFilter(request.query_params, queryset=comments)
            filtered_comments = comment_filter.qs

            # Verificar si se ha pasado un id para mostrar primero
            highlight_id = request.query_params.get('highlight_id')  # Asumiendo que el ID se pasará como 'id'
            if highlight_id:
                try:
                    specific_comment = filtered_comments.get(id=highlight_id)
                    filtered_comments = filtered_comments.exclude(id=highlight_id)  # Excluirlo de la lista
                    # Agregar el comentario específico al principio
                    filtered_comments = [specific_comment] + list(filtered_comments)
                except Comment.DoesNotExist:
                    pass  # Si no existe, simplemente ignorar

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_comments = pagination.paginate_queryset(filtered_comments, request)
                serializer = CommentSerializer(paginated_comments, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})

            serializer = CommentSerializer(filtered_comments, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            comment_id = request.data.get('comment_id')
            post_id = request.data.get('post_id')
            if comment_id and not Comment.objects.filter(pk=comment_id).exists():
                return Response(
                    {'error': 'El ID del comentario no está registrado.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            # Separar el archivo y otros datos
            file_data = request.FILES.get('file')  # Obtiene el archivo, si existe
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            try:
                blocked_id = Status.objects.get(name='Bloqueado').id

                # Verificar si el post está bloqueado
                if post_id:
                    post = Post.objects.get(id=post_id)
                    if post.status_id == blocked_id:
                        return Response(status=status.HTTP_204_NO_CONTENT)
                
                # Verificar si el comment está bloqueado
                if comment_id:
                    comment = Comment.objects.get(id=comment_id)
                    if comment.status_id == blocked_id:
                        return Response(status=status.HTTP_204_NO_CONTENT)

                # Buscar el ID del estado cuyo nombre es 'Activo'
                active_status = Status.objects.get(name__iexact='activo')
                other_data['status_id'] = active_status.id
            except ObjectDoesNotExist:
                # Manejar el caso en que no exista un estado llamado 'Activo'
                return Response({'error': 'Estado "Activo" no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Asignar el ID del usuario
            other_data['user_id'] = request.user.id
            
            # Crear una instancia del serializer con los datos restantes
            serializer = CommentSerializer(data=other_data)

            if serializer.is_valid():
                errors = {}

                # Validar que si no hay archivo, el campo body sea requerido
                if not file_data and not request.data.get('body'):
                    errors['body'] = ['Este campo no puede estar en blanco.']

                if errors:
                    return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

                # Guardar el comentario
                comment_instance = serializer.save()

                # Si hay un archivo, procesarlo y guardarlo
                if file_data:
                    # Lógica para guardar el archivo usando FileUploadMixin
                    file_info = self.put_file(file_data, 'comments')

                    # Crear instancia de File asociada al comentario
                    File.objects.create(
                        content_object=comment_instance,  # Relaciona el archivo con el comentario
                        path=file_info['path'],
                        extension=file_info['extension'],
                        size=file_info['size'],
                        type=file_info['type']
                    )

                return Response({'message': 'Comentario creado exitosamente.'}, status=status.HTTP_201_CREATED)

            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejo de excepciones
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Comentarios
#-----------------------------------------------------------------------------------------------------
class CommentDetailAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_comment'

    def get(self, request, pk):
        try:
            # Obtener el comentario usando el pk
            comment = Comment.objects.get(pk=pk)

            # Serializar los datos del comentario
            serializer = CommentSerializer(comment, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Comment.DoesNotExist:
            return Response({'error': 'El ID del comentario no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
    def put(self, request, pk):
        try:
            # Obtener el comentario usando el pk
            comment = Comment.objects.get(pk=pk)

            # Obtener el nuevo valor para `body`
            new_body = request.data.get('body')

            # Validar que el campo `body` sea proporcionado si no hay un archivo adjunto
            if not new_body and not comment.file.exists():
                return Response({'validation': {'body': ['Este campo no puede estar en blanco.']}}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar el campo `body` si se proporciona un nuevo valor
            if new_body is not None:
                comment.body = new_body

            # Guardar los cambios en el comentario
            comment.save()

            # Serializar los datos actualizados del comentario
            serializer = CommentSerializer(comment, context={'request': request})

            return Response({'message': 'Comentario actualizado exitosamente.'}, status=status.HTTP_200_OK)

        except Comment.DoesNotExist:
            return Response({'error': 'El ID de comentario no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def delete(self, request, pk):
        try:
            # Obtener el comentario usando el pk
            comment = Comment.objects.get(pk=pk)
            has_files = comment.file.exists()  # Verificar si el comentario tiene archivos asociados

            # Eliminar archivos asociados si existen
            if has_files:
                files = comment.file.all()  # Obtener todos los archivos asociados al comentario
                for file in files:
                    self.delete_file(file.path)  # Eliminar el archivo del sistema
                    file.delete()  # Eliminar el registro del archivo de la base de datos

            # Eliminar el comentario
            comment.delete()

            return Response({'message': 'El comentario ha sido eliminado correctamente.'}, status=status.HTTP_202_ACCEPTED)

        except Comment.DoesNotExist:
            return Response({'error': 'El ID del comentario no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)    
        
#-----------------------------------------------------------------------------------------------------
# Historias
#-----------------------------------------------------------------------------------------------------
class StoryIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_story'

    def get(self, request):
        try:
            # Obtener el usuario en sesión
            current_user = request.user

            limit_date = timezone.now() - timedelta(hours=24)
            Story.objects.filter(created_at__lt=limit_date).delete()

            # Excluir historias del usuario actual y que no estén bloqueadas
            stories = Story.objects.exclude(user=current_user).exclude(status__name__iexact='bloqueado').order_by('-created_at')

            # Filtrar historias según los parámetros de la solicitud
            story_filter = StoryFilter(request.query_params, queryset=stories)
            filtered_stories = story_filter.qs

            # Obtener todas las historias vistas por el usuario actual
            viewed_story_ids = set(StoryView.objects.filter(user=current_user).values_list('story_id', flat=True))

            # Agrupar historias por usuario
            grouped_stories = {}
            for story in filtered_stories:
                user_id = story.user.id
                if user_id not in grouped_stories:
                    grouped_stories[user_id] = {
                        'user': get_user_with_profile_photo(story.user, {'request': request}),
                        'stories': [],
                    }

                # Serializar la historia y marcarla como leída o no
                serialized_story = StorySerializer(story, context={'request': request}).data
                serialized_story['is_read'] = story.id in viewed_story_ids

                # Añadir la historia a la lista de historias del usuario
                grouped_stories[user_id]['stories'].append(serialized_story)

            # Convertir el diccionario a una lista para mantener el orden de los usuarios tal cual se obtuvieron
            grouped_stories_list = []
            for user_data in grouped_stories.values():
                # Ordenar las historias de cada usuario de la más vieja a la más nueva (usando 'created_at')
                user_data['stories'].sort(key=lambda x: x['attributes']['created_at'])

                # Determinar si todas las historias del usuario están leídas
                all_stories_read = all(story['is_read'] for story in user_data['stories'])
                user_data['all_read'] = all_stories_read

                # Añadir el dato procesado a la lista
                grouped_stories_list.append(user_data)

            # Separar los grupos según si todas las historias están leídas
            unread_groups = [user_data for user_data in grouped_stories_list if not user_data['all_read']]
            read_groups = [user_data for user_data in grouped_stories_list if user_data['all_read']]

            # Combinar grupos de forma que los grupos no leídos estén primero
            final_grouped_stories_list = unread_groups + read_groups

            # Verificar si se requiere paginación
            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_stories = pagination.paginate_queryset(final_grouped_stories_list, request)
                return pagination.get_paginated_response({'data': paginated_stories})

            return Response({'data': final_grouped_stories_list}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):# Esto te ayudará a ver qué datos estás recibiendo
        try:
            # Separar el archivo y otros datos
            file_data = request.FILES.get('file')  
            content_data = request.data.get('content')
            post_id = request.data.get('post_id')
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            try:
                # Buscar el ID del estado cuyo nombre es 'Activo'
                active_status = Status.objects.get(name__iexact='activo')
                other_data['status_id'] = active_status.id
            except ObjectDoesNotExist:
                # Manejar el caso en que no exista un estado llamado 'Activo'
                return Response({'error': 'Estado "Activo" no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Asignar el ID del usuario
            other_data['user_id'] = request.user.id
            
            # Crear una instancia del serializer con los datos restantes
            serializer = StorySerializer(data=other_data)

            if serializer.is_valid():
                errors = {}

                # Validar que se proporcione al menos uno de los campos
                if not file_data and not (content_data or post_id):
                    errors['content'] = ['Este campo no puede estar en blanco.']
                
                if errors:
                    return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

                # Guardar la historia
                story_instance = serializer.save()

                # Si hay un archivo, procesarlo y guardarlo
                if file_data:
                    # Lógica para guardar el archivo usando FileUploadMixin
                    file_info = self.put_file(file_data, 'stories')

                    # Crear instancia de File asociada a la historia
                    File.objects.create(
                        content_object=story_instance,  # Relaciona el archivo con la historia
                        path=file_info['path'],
                        extension=file_info['extension'],
                        size=file_info['size'],
                        type=file_info['type']
                    )

                return Response({'message': 'Historia creada exitosamente.'}, status=status.HTTP_201_CREATED)

            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return handle_exception(e)

class StoryViewIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_storyview'

    def get(self, request):
        try:
            # Obtener todas las vistas de historia, excluyendo al usuario creador
            storyViews = StoryView.objects.all().order_by('-created_at')
            storyViews_filter = StoryViewFilter(request.query_params, queryset=storyViews)
            filtered_storyViews = storyViews_filter.qs

            # Obtener los IDs de las historias vistas
            story_ids = filtered_storyViews.values_list('story_id', flat=True).distinct()

            # Obtener los IDs de los creadores de las historias
            creators = Story.objects.filter(id__in=story_ids).values_list('user_id', flat=True)

            # Filtrar las vistas para excluir las del creador
            filtered_storyViews = filtered_storyViews.exclude(user__id__in=creators)

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_storyViews = pagination.paginate_queryset(filtered_storyViews, request)
                serializer = StoryViewSerializer(paginated_storyViews, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = StoryViewSerializer(filtered_storyViews, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
        
    def post(self, request):
        try:
            story_ids = request.data.get('story_ids', [])

            user = request.user

            registered_stories = []

            for story_id in story_ids:
                try:
                    story = Story.objects.get(id=story_id)
                except ObjectDoesNotExist:
                    continue

                story_view_exists = StoryView.objects.filter(user=user, story=story).exists()

                if not story_view_exists:
                    StoryView.objects.create(user=user, story=story)
                    registered_stories.append(story_id)

            if registered_stories:
                message = f'Vistas de las historias {registered_stories} registradas exitosamente.'
                return Response({'message': message}, status=status.HTTP_201_CREATED)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return handle_exception(e)



class StoryViewCountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            story_id = request.data.get('story_id')

            if not story_id:
                return Response({'validation': 'La historia es requerida.'}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener la historia para acceder al user_id del propietario
            story = Story.objects.get(id=story_id)

            # Contar las visualizaciones, excluyendo al propietario
            count = StoryView.objects.filter(story__id=story_id).exclude(user_id=story.user_id).count()

            return Response({'message': count}, status=status.HTTP_200_OK)

        except Story.DoesNotExist:
            return Response({'validation': 'La historia no existe.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)


class StoryGroupedAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_story' 
        
    def get(self, request, user_id):
        try:
            # Excluir historias que estén bloqueadas
            stories = Story.objects.exclude(status__name__iexact='bloqueado').filter(user_id=user_id).order_by('-created_at')

            if not stories.exists():
                return Response({'error': 'El usuario no tiene historias.'}, status=status.HTTP_404_NOT_FOUND)

            # Obtener el usuario en sesión
            current_user = request.user
            
            # Obtener todas las historias vistas por el usuario actual
            viewed_story_ids = set(StoryView.objects.filter(user=current_user).values_list('story_id', flat=True))

            # Agrupar historias por el usuario especificado (solo hay un usuario)
            grouped_stories = {
                'user': get_user_with_profile_photo(stories.first().user, {'request': request}),
                'stories': [],
                'all_read': False
            }

            # Agregar cada historia del usuario al grupo
            for story in stories:
                # Serializar la historia y marcarla como leída o no
                serialized_story = StorySerializer(story, context={'request': request}).data
                serialized_story['is_read'] = story.id in viewed_story_ids

                # Añadir la historia a la lista de historias del usuario
                grouped_stories['stories'].append(serialized_story)

            # Ordenar las historias del usuario de la más vieja a la más nueva
            grouped_stories['stories'].sort(key=lambda x: x['attributes']['created_at'])

            # Verificar si todas las historias del usuario están leídas
            grouped_stories['all_read'] = all(story['is_read'] for story in grouped_stories['stories'])

            # Devolver el objeto como respuesta, no como lista
            return Response({'data': grouped_stories}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Historias
#-----------------------------------------------------------------------------------------------------
class StoryDetailAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_story'

    def get(self, request, pk):
        try:
            # Obtener la historia usando el pk
            story = Story.objects.get(pk=pk)

            # Serializar los datos de la historia
            serializer = StorySerializer(story, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except story.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def put(self, request, pk):
        try:
            # Obtener la historia usando el pk
            story = Story.objects.get(pk=pk)

            if story.archive:
                story.archive = False
                story.restore()  # Restaurar si ya estaba archivada
                message = 'La historia ha sido desarchivada correctamente.'
            else:
                story.archive = True
                story.soft_delete()  # Archivar si no estaba archivada
                message = 'La historia ha sido archivada correctamente.'

            # Guardar los cambios
            story.save()

            return Response({'message': message}, status=status.HTTP_200_OK)

        except story.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
    def delete(self, request, pk):
        try:
            # Obtener el comentario usando el pk
            story = Story.objects.get(pk=pk)
            has_files = story.file.exists()  # Verificar si la historia tiene archivos asociados

            # Eliminar archivos asociados si existen
            if has_files:
                files = story.file.all()  # Obtener todos los archivos asociados a la historia
                for file in files:
                    self.delete_file(file.path)  # Eliminar el archivo del sistema
                    file.delete()  # Eliminar el registro del archivo de la base de datos

            # Eliminar la historia
            story.delete()

            return Response({'message': 'La historia ha sido eliminada correctamente.'}, status=status.HTTP_202_ACCEPTED)

        except Story.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e) 
        
#-----------------------------------------------------------------------------------------------------
# Notificaciones
#-----------------------------------------------------------------------------------------------------
class NotificationShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk)

            serializer = NotificationSerializer(notification, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Notification.DoesNotExist:
            return Response({'error': 'La notificación no está registrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)

class NotificationIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            notifications = Notification.objects.all().order_by('-created_at')
            notification_filter = NotificationFilter(request.GET, queryset=notifications)

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_notifications = pagination.paginate_queryset(notification_filter.qs, request)
                serializer = NotificationSerializer(paginated_notifications, many=True, context={'request': request})
                return pagination.get_paginated_response({'data': serializer.data})

            serializer = NotificationSerializer(notification_filter.qs, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

class NotificationCountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            type = request.data.get('type')

            if not type:
                return Response({'validation': 'El parámetro "type" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

            count = Notification.objects.filter(type__startswith=type).count()

            return Response({'message': count}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)


class NotificationViewIndexAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            id = request.data.get('id')
            model_name = request.data.get('model')
            object_id = request.data.get('object_id')

            try:
                content_type = ContentType.objects.get(model=model_name.lower())
            except ContentType.DoesNotExist:
                return Response({'validation': f'El modelo "{model_name}" no existe.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                notification = Notification.objects.get(object_id=object_id, content_type_id=content_type.id, id=id)

                if not notification.is_read:
                    notification.is_read = True
                    notification.save()
                    return Response({'message': 'La notificación ha sido marcada como leída.'}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message': 'La notificación ya está marcada como leída.'}, status=status.HTTP_202_ACCEPTED)
                
            except ObjectDoesNotExist:
                return Response({'error': f'Notification con ID {object_id} no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            # Esta línea ha sido eliminada
            # return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return handle_exception(e)


class ReadNotificationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            notifications = Notification.objects.filter(receiver_user=user, is_read=False)

            if not notifications.exists():
                return Response({'message': 'No hay notificaciones pendientes por leer.'}, status=status.HTTP_202_ACCEPTED)

            notifications.update(is_read=True)

            return Response({'message': 'Todas las notificaciones han sido marcadas como leídas.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

class SeenNotificationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            notifications = Notification.objects.filter(receiver_user=user, is_seen=False)

            if not notifications.exists():
                return Response({'message': 'No hay notificaciones sin ver.'}, status=status.HTTP_202_ACCEPTED)

            notifications.update(is_seen=True)

            return Response({'message': 'Todas las notificaciones han sido marcadas como vistas.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e)

class NotificationDeleteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk)

            notification.delete()

            return Response({'message': 'Notificación eliminada exitosamente.'}, status=status.HTTP_202_ACCEPTED)

        except Notification.DoesNotExist:
            return Response({'error': f'Notificación con ID {pk} no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Informacion de las sesiones
#-----------------------------------------------------------------------------------------------------

class SessionInfoAPI(APIView):
    def post(self, request):
        try:
            session_key = request.data.get('session_key')
            user_id = request.data.get('user_id')
            session_exists = SessionInfo.objects.filter(
                session_key=session_key,
                user_id=user_id
            ).exists()
            if session_exists:
                return Response({'exists': True}, status=status.HTTP_200_OK)
            return Response({'exists': False}, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_exception(e)

        
