from rest_framework import serializers
from django.contrib.auth.models import *
from .models import *
from django.contrib.auth.hashers import make_password

#-----------------------------------------------------------------------------------------------------
# Grupo o Roles
#-----------------------------------------------------------------------------------------------------
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'name': representation['name'],
            },
        }

#-----------------------------------------------------------------------------------------------------
# Paises
#-----------------------------------------------------------------------------------------------------

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id',
                'name', 
                'abbreviation', 
                'dialing_code',
                'created_at',
                'updated_at', 
                )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'name': representation['name'],
                'abbreviation': representation['abbreviation'],
                'dialing_code': representation['dialing_code'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
        
#-----------------------------------------------------------------------------------------------------
# Archivos
#-----------------------------------------------------------------------------------------------------
class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ('id', 
                'content_type',
                'object_id',
                'path',
                'extension',
                'size',
                'type',
                'url',
                'created_at',
                'updated_at',
                'deleted_at',
                )
        
    def get_url(self, obj):
        if obj is not None and obj.path:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(settings.MEDIA_URL + obj.path)
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'content_type': representation['content_type'],
                'object_id': representation['object_id'],
                'path': representation['path'],
                'extension': representation['extension'],
                'size': representation['size'],
                'type': representation['type'],
                'url': representation['url'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
#-----------------------------------------------------------------------------------------------------
# Funcion para usuario con la foto de perfil
#-----------------------------------------------------------------------------------------------------

def get_user_with_profile_photo(user, context):
    # Obtener el archivo de perfil del usuario
    profile_file = user.files.filter(type='profile').first()
    profile_photo_url = None
    if profile_file:
        request = context.get('request')
        if request:
            profile_photo_url = request.build_absolute_uri(settings.MEDIA_URL + profile_file.path)
    
    return {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'profile_photo_url': profile_photo_url
    }
    
#-----------------------------------------------------------------------------------------------------
# Seguimientos
#-----------------------------------------------------------------------------------------------------
class FollowSerializer(serializers.ModelSerializer):
    following_user = serializers.SerializerMethodField()
    followed_user = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 
                'following_user',
                'followed_user',
                'created_at',
                'updated_at',
                )

    def get_following_user(self, obj):
        return self.get_user_with_profile_photo(obj.following_user)

    def get_followed_user(self, obj):
        return self.get_user_with_profile_photo(obj.followed_user)

    def get_user_with_profile_photo(self, user):
        # Obtener el archivo de perfil del usuario
        profile_file = user.files.filter(type='profile').first()
        profile_photo_url = None
        if profile_file:
            request = self.context.get('request')
            if request:
                profile_photo_url = request.build_absolute_uri(settings.MEDIA_URL + profile_file.path)
        
        return {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'profile_photo_url': profile_photo_url
        }
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'following_user': representation['following_user'],
                'followed_user': representation['followed_user'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
        
#-----------------------------------------------------------------------------------------------------
# Reacciones
#-----------------------------------------------------------------------------------------------------
class ReactionSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, allow_null=True, source='user')

    class Meta:
        model = Reaction
        fields = (
            'id', 
            'content_type',
            'object_id',
            'user_id',
            'created_at',
            'updated_at',
            'deleted_at',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        return {
            'id': representation['id'],
            'attributes': {
                'content_type': representation['content_type'],
                'object_id': representation['object_id'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
            }
        }
        
#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------
class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = (
            'id', 
            'content_type',
            'object_id',
            'observation',
            'created_at',
            'updated_at',
            'deleted_at',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        return {
            'id': representation['id'],
            'attributes': {
                'content_type': representation['content_type'],
                'object_id': representation['object_id'],
                'observation': representation['observation'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
            }
        }

#-----------------------------------------------------------------------------------------------------
# Usuarios
#-----------------------------------------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), write_only=True, allow_null=True, source='country')
    files = FileSerializer(many=True, read_only=True)
    
    # Campos añadidos para los seguidores y seguidos
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id',
                'email', 
                'username',  
                'name', 
                'country_id',
                'biography',
                'phone_number',
                'is_active',
                'is_staff',
                'created_at',
                'updated_at',
                'deleted_at',  
                'country',
                'birthdate',
                'groups',
                'files',
                'following',    
                'followers'
                ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'username': representation['username'],
                'name': representation['name'],
                'email': representation['email'],
                'biography': representation['biography'],
                'phone_number': representation['phone_number'],
                'birthdate': representation['birthdate'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'country': representation['country'],
                'groups': representation['groups'],
                'files': representation['files'],
                'following': representation['following'],
                'followers': representation['followers']
            }
        }
        
    def get_following(self, obj):
        follows = Follow.objects.filter(following_user=obj)
        return FollowSerializer(follows, many=True, context=self.context).data

    def get_followers(self, obj):
        follows = Follow.objects.filter(followed_user=obj)
        return FollowSerializer(follows, many=True, context=self.context).data
        
#-----------------------------------------------------------------------------------------------------
# Registro de usuario
#-----------------------------------------------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), write_only=True, source='country', required=False
    )

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe ser alfanumérica.")
        return value

    def create(self, validated_data):
        default_group = Group.objects.get(id=3)  # Asegúrate de que este ID sea correcto y exista en tu base de datos
        validated_data['password'] = make_password(validated_data['password'])  # Cifra la contraseña
        validated_data['username'] = validated_data['username'].lower()  # Convierte el nombre de usuario a minúsculas
        
        # Elimina 'country' de validated_data si no está presente
        country = validated_data.pop('country', None)

        user = super().create(validated_data)
        user.groups.add(default_group)  # Asocia el grupo por defecto al usuario
        
        # Asigna el país al usuario si se proporcionó
        if country:
            user.country = country
            user.save()

        return user
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'biography', 'password', 'phone_number',
                'birthdate', 'country_id', 'is_active', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True},
            'biography': {'required': False},
            'phone_number': {'required': False},
            'birthdate': {'required': True},
        }

#-----------------------------------------------------------------------------------------------------
# Estados
#-----------------------------------------------------------------------------------------------------

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('id',
                'name', 
                'description', 
                'created_at',
                'updated_at', 
                'deleted_at',
                )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'name': representation['name'],
                'description': representation['description'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
        
#-----------------------------------------------------------------------------------------------------
# Tipos de publicación
#-----------------------------------------------------------------------------------------------------

class TypePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePost
        fields = ('id',
                'name', 
                'description', 
                'created_at',
                'updated_at', 
                'deleted_at',
                )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'name': representation['name'],
                'description': representation['description'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }