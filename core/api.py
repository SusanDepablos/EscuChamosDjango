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
    # Validar nueva contraseña
    if len(new_password) < 8:
        return {'validation': 'La nueva contraseña debe tener al menos 8 caracteres.'}, status.HTTP_400_BAD_REQUEST

    if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
        return {'validation': 'La nueva contraseña debe ser alfanumérica.'}, status.HTTP_400_BAD_REQUEST

    # Actualizar la contraseña
    user.password = make_password(new_password)
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
        
        # Asegúrate de que el modelo tenga un campo de estado y actualízalo
        if hasattr(obj, 'status'):
            obj.status = Status.objects.get(id=status_id)  # Obtén el estado por ID
            obj.save()
            return Response({'message': 'Reporte creado exitosamente.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'El objeto no tiene un campo de estado.'}, status=status.HTTP_404_BAD_REQUEST)
    except model_class.DoesNotExist:
        return Response({'error': 'El objeto relacionado no se encontró.'}, status=status.HTTP_404_NOT_FOUND)
    except Status.DoesNotExist:
        return Response({'error': 'Estatus no encontrado.'}, status=status.HTTP_404_BAD_REQUEST)

#-----------------------------------------------------------------------------------------------------
# Autenticación
#-----------------------------------------------------------------------------------------------------   

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
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    groups = user.groups.values_list('id', flat=True)  # Obtiene los nombres de los grupos del usuario
                    return Response({
                        'message': 'Inicio de sesión exitoso.',
                        'token': token.key,
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
            Token.objects.filter(user=request.user).delete()
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

        if not new_password:
            return Response({'validation': 'El campo contraseña es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'message': 'Usuario actualizado exitosamente.'}, status=status.HTTP_200_OK)
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

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'validation': 'Los campos de contraseña anterior y nueva contraseña son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validar la contraseña anterior
            if not check_password(old_password, user.password):
                return Response({'validation': 'La contraseña anterior no es correcta.'}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'message': 'La foto ha sido eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'No se encontró la foto.'}, status=status.HTTP_404_NOT_FOUND)

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
                return Response({'error': 'Ya sigues a este usuario.'}, status=status.HTTP_409_CONFLICT)

            # Crear una nueva relación de seguimiento
            follow_instance = Follow.objects.create(following_user=user, followed_user=followed_user)

            # Serializar la relación creada
            serializer = FollowSerializer(follow_instance)

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
    
    def delete(self, request, pk):
        try:
            # Obtener el usuario autenticado
            user = request.user
            
            # Obtener el usuario a dejar de seguir usando el pk en la URL
            followed_user = User.objects.get(id=pk)
            
            if user.id == followed_user.id:
                return Response({'validation': 'No puedes dejar de seguirte a ti mismo.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si existe una relación de seguimiento
            follow_instance = Follow.objects.filter(following_user=user, followed_user=followed_user).first()

            if not follow_instance:
                return Response({'validation': 'No estás siguiendo a este usuario.'}, status=status.HTTP_400_BAD_REQUEST)

            # Eliminar la relación de seguimiento
            follow_instance.delete()

            return Response({'message': 'Has dejado de seguir a este usuario.'}, status=status.HTTP_204_NO_CONTENT)
        
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
            reaction = Reaction.objects.all()

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_reaction = pagination.paginate_queryset(reaction, request)
                serializer = ReactionSerializer(paginated_reaction, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ReactionSerializer(reaction, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
    def post(self, request):
        user = request.user
        data = request.data.copy()  # Copia los datos del request para agregar el usuario
        data['user'] = user.id  # Agrega el ID del usuario al diccionario de datos

        # Validar content_type y object_id
        content_type_id = data.get('content_type')
        object_id = data.get('object_id')

        # Inicializamos variables para verificar el content_type y object_id
        content_type = None
        obj = None

        try:
            # Verificar que el ContentType exista
            content_type = ContentType.objects.get(id=content_type_id)

            # Verificar que el objeto relacionado exista
            model_class = content_type.model_class()
            obj = model_class.objects.get(id=object_id)
                    # Si ambas validaciones son exitosas, proceder con la serialización y guardado
            serializer = ReactionSerializer(data=data)  # Pasa los datos con el usuario al serializer

            if serializer.is_valid():
                reaction = serializer.save()  # Guarda la reacción
                return Response({'message': 'Reacción creada exitosamente.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except ContentType.DoesNotExist:
            return Response({'error': 'ContentType no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

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
        
    def delete(self, request, pk):
        try:
            # Obtener la reacción usando el pk
            reaction = Reaction.objects.get(pk=pk)
            
            # Verifica si el usuario autenticado es el propietario de la reacción
            if reaction.user != request.user:
                return Response({'error': 'No tienes permiso para eliminar esta reacción.'}, status=status.HTTP_403_FORBIDDEN)

            # Eliminar la reacción
            reaction.delete()

            return Response({'message': 'La reacción ha sido eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)

        except Reaction.DoesNotExist:
            return Response({'error': 'El ID de la reacción no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------
class ReportIndexCreateAPIView(APIView):
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
    def post(self, request):
        try:
            user = request.user
            data = request.data.copy()  # Copia los datos del request para agregar el usuario
            data['user'] = user.id  # Agrega el ID del usuario al diccionario de datos

            serializer = ReportSerializer(data=data)  # Pasa los datos con el usuario al serializer
            if serializer.is_valid():
                report = serializer.save()  # Guarda el reporte

                # Llama a la función para actualizar el estado del objeto
                response = update_object_status(
                    report.content_type.id, 
                    report.object_id, 
                    2  # Estatus 2 "Reportado"
                )
                
                return response  # Retorna la respuesta de la función
            else:
                return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
        
#-----------------------------------------------------------------------------------------------------
# Publicaciones
#-----------------------------------------------------------------------------------------------------
class PostIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_post'

    def get(self, request):
        try:
            posts = Post.objects.all()

            post_filter = PostFilter(request.query_params, queryset=posts)
            filtered_post = post_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_post = pagination.paginate_queryset(filtered_post, request)
                serializer = PostSerializer(paginated_post, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = PostSerializer(filtered_post, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            # Obtener el post_id de la publicación padre desde request.data
            post_id = request.data.get('post_id')
            
            if post_id and not Post.objects.filter(pk=post_id).exists():
                return Response(
                    {'error': 'El ID de la publicación no está registrado.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Separar archivos y otros datos
            file_list = request.FILES.getlist('file')  # Obtiene la lista de archivos, si existen
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            other_data['user_id'] = request.user.id
            other_data['status_id'] = 1

            # Crear una instancia del serializer con los datos restantes
            serializer = PostSerializer(data=other_data)

            if serializer.is_valid():
                type_post_id = int(request.data.get('type_post_id')[0])
                errors = {}

                if type_post_id == 2 and not file_list:
                    errors['file'] = ['Este campo es requerido.']

                if type_post_id == 1 and not request.data.get('body'):
                    errors['body'] = ['Este campo es requerido.']

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
                return Response({'validation': {'body': ['Este campo es requerido.']}}, status=status.HTTP_400_BAD_REQUEST)

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

            return Response({'message': 'La publicación ha sido eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)

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
            shares = Share.objects.all()

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_share = pagination.paginate_queryset(shares, request)
                serializer = ShareSerializer(paginated_share, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = ShareSerializer(shares, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            data = request.data.copy()
            data['user_id'] = request.user.id

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
            return Response({'message': 'El compartido ha sido eliminado exitosamente.'}, status=status.HTTP_204_NO_CONTENT)

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
            comments = Comment.objects.all()

            comment_filter = CommentFilter(request.query_params, queryset=comments)
            filtered_comment = comment_filter.qs

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_comment = pagination.paginate_queryset(filtered_comment, request)
                serializer = CommentSerializer(paginated_comment, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = CommentSerializer(filtered_comment, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            comment_id = request.data.get('comment_id')
            if comment_id and not Comment.objects.filter(pk=comment_id).exists():
                return Response(
                    {'error': 'El ID del comentario no está registrado.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            # Separar el archivo y otros datos
            file_data = request.FILES.get('file')  # Obtiene el archivo, si existe
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            other_data['user_id'] = request.user.id
            other_data['status_id'] = 1

            # Crear una instancia del serializer con los datos restantes
            serializer = CommentSerializer(data=other_data)

            if serializer.is_valid():
                errors = {}

                # Validar que si no hay archivo, el campo body sea requerido
                if not file_data and not request.data.get('body'):
                    errors['body'] = ['Este campo es requerido.']

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

        except comment.DoesNotExist:
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
                return Response({'validation': {'body': ['Este campo es requerido.']}}, status=status.HTTP_400_BAD_REQUEST)

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

            return Response({'message': 'El comentario ha sido eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist:
            return Response({'error': 'El ID del comentario no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)    
        
#-----------------------------------------------------------------------------------------------------
# Historias
#-----------------------------------------------------------------------------------------------------
class HistoryIndexCreateAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_history'

    def get(self, request):
        try:
            histories = History.objects.all()

            if 'pag' in request.query_params:
                pagination = CustomPagination()
                paginated_history = pagination.paginate_queryset(histories, request)
                serializer = CommentSerializer(paginated_history, many=True)
                return pagination.get_paginated_response({'data': serializer.data})
            
            serializer = HistorySerializer(histories, many=True, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return handle_exception(e)
            
    def post(self, request):
        try:
            # Separar el archivo y otros datos
            file_data = request.FILES.get('file')  
            content_data = request.data.get('content')
            post_id = request.data.get('post_id')
            other_data = {k: v for k, v in request.data.items() if k != 'file'}

            # Asignar datos adicionales al diccionario
            other_data['user_id'] = request.user.id
            other_data['status_id'] = 1
            
            # Crear una instancia del serializer con los datos restantes
            serializer = HistorySerializer(data=other_data)

            if serializer.is_valid():
                errors = {}

                # Validar que se proporcione al menos uno de los campos
                if not file_data and not (content_data or post_id):
                    errors['content'] = ['Este campo es requerido.']
                
                if errors:
                    return Response({'validation': errors}, status=status.HTTP_400_BAD_REQUEST)

                # Guardar la historia
                history_instance = serializer.save()

                # Si hay un archivo, procesarlo y guardarlo
                if file_data:
                    # Lógica para guardar el archivo usando FileUploadMixin
                    file_info = self.put_file(file_data, 'histories')

                    # Crear instancia de File asociada a la historia
                    File.objects.create(
                        content_object=history_instance,  # Relaciona el archivo con la historia
                        path=file_info['path'],
                        extension=file_info['extension'],
                        size=file_info['size'],
                        type=file_info['type']
                    )

                return Response({'message': 'Historia creada exitosamente.'}, status=status.HTTP_201_CREATED)

            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejo de excepciones
            return handle_exception(e)
        
#-----------------------------------------------------------------------------------------------------
# Información de Historias
#-----------------------------------------------------------------------------------------------------
class HistoryDetailAPIView(APIView, FileUploadMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_history'

    def get(self, request, pk):
        try:
            # Obtener la historia usando el pk
            history = History.objects.get(pk=pk)

            # Serializar los datos de la historia
            serializer = HistorySerializer(history, context={'request': request})

            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

        except history.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
    def put(self, request, pk):
        try:
            # Obtener la historia usando el pk
            history = History.objects.get(pk=pk)

            if history.archive:
                history.archive = False
                history.restore()  # Restaurar si ya estaba archivada
                message = 'La historia ha sido desarchivada correctamente.'
            else:
                history.archive = True
                history.soft_delete()  # Archivar si no estaba archivada
                message = 'La historia ha sido archivada correctamente.'

            # Guardar los cambios
            history.save()

            return Response({'message': message}, status=status.HTTP_200_OK)

        except History.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e)
        
    def delete(self, request, pk):
        try:
            # Obtener el comentario usando el pk
            history = History.objects.get(pk=pk)
            has_files = history.file.exists()  # Verificar si la historia tiene archivos asociados

            # Eliminar archivos asociados si existen
            if has_files:
                files = history.file.all()  # Obtener todos los archivos asociados a la historia
                for file in files:
                    self.delete_file(file.path)  # Eliminar el archivo del sistema
                    file.delete()  # Eliminar el registro del archivo de la base de datos

            # Eliminar la historia
            history.delete()

            return Response({'message': 'La historia ha sido eliminada correctamente.'}, status=status.HTTP_204_NO_CONTENT)

        except History.DoesNotExist:
            return Response({'error': 'El ID de la historia no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e) 
        
