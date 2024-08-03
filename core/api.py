from .models import *
from .serializer import *
from .mixins import *
from .filters import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string

#-----------------------------------------------------------------------------------------------------
# Paginación 
#-----------------------------------------------------------------------------------------------------

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pag'
    
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
                        'groups': list(groups),  # Convertir a lista para la respuesta JSON
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Este usuario está inactivo'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Nombre de usuario o contraseña inválidos.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                    return Response({
                        'data': {
                            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                            'title': ['Se produjo un error interno'],
                            'errors': str(e)
                        }
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                return Response({
                    'data': {
                        'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'title': ['Se produjo un error interno'],
                        'errors': str(e)
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-----------------------------------------------------------------------------------------------------
# Función para enviar Email con código
#-----------------------------------------------------------------------------------------------------
def send_verification_email(user_email, username, verification_code):
    subject = 'Verifica tu dirección de correo electrónico'
    html_content = render_to_string('verify_email.html', {'username': username, 'verification_code': verification_code, 'user_email': user_email})
    send_mail(
        subject,
        '',
        'escuchamos2024@gmail.com', 
        [user_email],
        html_message=html_content,
    )

#-----------------------------------------------------------------------------------------------------
# Registrarse
#-----------------------------------------------------------------------------------------------------
class UserRegisterAPIView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                user = serializer.save(verification_code=verification_code, is_active=False)
                send_verification_email(user.email, user.username, verification_code)
                
                return Response({'message': 'Se ha enviado un correo electrónico de verificación'}, status=status.HTTP_200_OK)
            return Response({'validation': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#-----------------------------------------------------------------------------------------------------
# Reenviar código
#-----------------------------------------------------------------------------------------------------      
class ResendVerificationCodeAPIView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get('user_email')
            if not user_email:
                return Response({'error': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(email=user_email).first()
            
            if user and not user.is_email_verified:
                # Generar un nuevo código de verificación
                new_verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                user.verification_code = new_verification_code
                user.save()
                
                # Enviar el nuevo código por correo electrónico
                send_verification_email(user.email, user.username, new_verification_code)
                
                return Response({'message': 'Se ha enviado un nuevo correo electrónico de verificación'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
                return Response({'error': 'El código de verificación es incorrecto'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
                    return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-----------------------------------------------------------------------------------------------------
# Recuperar Cuenta
#-----------------------------------------------------------------------------------------------------
class RecoverAccountAPIView(APIView):
    def post(self, request):
        try:
            user_email = request.data.get('user_email')
            if not user_email:
                return Response({'error': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=user_email).first()

            if user:
                # Generar un nuevo código de verificación alfanumérico
                new_verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.verification_code = new_verification_code
                user.save()
                
                # Enviar el nuevo código por correo electrónico
                self.send_verification_email(user.email, user.username, new_verification_code)
                
                return Response({'message': 'Se ha enviado un correo electrónico de recuperación de cuenta'}, status=status.HTTP_200_OK)
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_verification_email(self, user_email, username, verification_code):
        subject = 'Recupera tu cuenta'
        html_content = render_to_string('recover_account_email.html', {'username': username, 'verification_code': verification_code, 'user_email': user_email})
        send_mail(
            subject,
            '',
            'escuchamos2024@gmail.com',
            [user_email],
            html_message=html_content,
        )
        
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
                    # Si el código es correcto pero el usuario ya está verificado
                    return Response({'message': 'El código ha sido verificado correctamente'}, status=status.HTTP_200_OK)
                
                # Si el código de verificación es correcto y el usuario no está verificado
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({'message': 'El código ha sido verificado correctamente'}, status=status.HTTP_200_OK)
            else:
                # Si el código de verificación es incorrecto
                return Response({'error': 'El código de verificación es incorrecto'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # Si el usuario no existe
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#-----------------------------------------------------------------------------------------------------
# Cambiar contraseña
#-----------------------------------------------------------------------------------------------------
class  RecoverAccountChangePasswordAPIView(APIView):
    def put(self, request):
        user_email = request.data.get('user_email')
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'validation': 'El campo contraseña es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=user_email)
            
            # Validar nueva contraseña
            if len(new_password) < 8:
                return Response({
                    'error': 'La nueva contraseña debe tener al menos 8 caracteres'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
                return Response({
                    'error': 'La nueva contraseña debe ser alfanumérica'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar la contraseña
            user.password = make_password(new_password)
            user.save()
            
            return Response({
                'message': 'Contraseña actualizada exitosamente'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-----------------------------------------------------------------------------------------------------
# Usuarios 
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
                return pagination.get_paginated_response({'users': serializer.data})
            
            serializer = UserSerializer(filtered_users, many=True, context={'request': request})
            return Response({'users': serializer.data})
        
        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UserShowAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # required_permissions = 'view_user'

    def get(self, request, pk):
        try:

            user = User.objects.filter(pk=pk).first()
            if not user:
                return Response({
                    'mensaje': 'El ID de usuario no está registrado'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user, context={'request': request})
            return Response({'data': serializer.data})

        except Exception as e:
            return Response({
                'data': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': ['Se produjo un error interno'],
                    'errors': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            