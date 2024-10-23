from rest_framework import serializers
from django.contrib.auth.models import *
from .models import *
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.db.models import Count

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
                'iso',
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
                'iso': representation['iso'],
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
        'profile_photo_url': profile_photo_url,
        'group_id': user.groups.values_list('id', flat=True)
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
        return get_user_with_profile_photo(obj.following_user, self.context)

    def get_followed_user(self, obj):
        return get_user_with_profile_photo(obj.followed_user, self.context)
        
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
    class Meta:
        model = Reaction
        fields = (
            'id', 
            'content_type',
            'object_id',
            'user',
            'created_at',
            'updated_at',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        return {
            'id': representation['id'],
            'attributes': {
                'content_type': representation['content_type'],
                'object_id': representation['object_id'],
                'user_id': instance.user.id,
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
            'user',
            'created_at',
            'updated_at',
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
                'user_id': instance.user.id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
            }
        }
        
class ReportGroupedSerializer(serializers.Serializer):
    content_type = serializers.IntegerField()
    object_id = serializers.IntegerField()
    reports_count = serializers.IntegerField()
    object_type = serializers.CharField()  # Campo adicional para el tipo de objeto

    def to_representation(self, instance):
        content_type_id = instance['content_type']
        object_id = instance['object_id']

        # Obtener el ContentType correspondiente
        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            content_type = None

        # Buscar el objeto correspondiente según el content_type
        if content_type:
            model_class = content_type.model_class()
            related_object = model_class.objects.filter(id=object_id).first()
        else:
            related_object = None

        # Definir las relaciones para 'post' y 'comment'
        post_representation = None
        comment_representation = None
        object_type = None  # Tipo de objeto

        # Verificar el tipo de objeto relacionado
        if isinstance(related_object, Comment):
            # Pasar solo el request al serializer de comentarios
            comment_representation = CommentSerializer(related_object, context={'request': self.context['request']}).data
            object_type = 'comment'  # Tipo de objeto

        elif isinstance(related_object, Post):
            # Pasar solo el request al serializer de publicaciones
            post_representation = PostSerializer(related_object, context={'request': self.context['request']}).data
            object_type = 'post'  # Tipo de objeto

            # Verificar si es un repost
            if related_object.post:  # Si hay un post original, es un repost
                object_type = 'repost'  # Tipo de objeto como repost

        # Formatear la respuesta con las relaciones
        return {
            'attributes': {
                'content_type': content_type_id,
                'object_id': object_id,
                'reports_count': instance['reports_count'],
                'object_type': object_type,  # Agregar el nuevo campo
            },
            'relationships': {
                'post': post_representation,
                'comment': comment_representation,
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
    
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    
    # Campos añadidos para los seguidores y seguidos
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'username',  
            'name', 
            'biography',
            'phone_number',
            'country_id',
            'country',
            'birthdate',
            'is_active',
            'is_staff',
            'created_at',
            'updated_at',
            'deleted_at',  
            'groups',
            'files',
            'following_count',
            'followers_count',
            'following',    
            'followers'
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        country_id = instance.country.id if instance.country else None
        
        return {
            'id': representation['id'],
            'attributes': {
                'username': representation['username'],
                'name': representation['name'],
                'email': representation['email'],
                'biography': representation['biography'],
                'phone_number': representation['phone_number'],
                'birthdate': representation['birthdate'],
                "country_id": country_id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'country': representation['country'],
                'groups': representation['groups'],
                'files': representation['files'],
                'following_count': representation['following_count'],
                'followers_count': representation['followers_count'],
                'following': representation['following'],
                'followers': representation['followers']
            }
        }

    # Métodos para contar seguidores y seguidos
    def get_following_count(self, obj):
        return Follow.objects.filter(following_user=obj).count()

    def get_followers_count(self, obj):
        return Follow.objects.filter(followed_user=obj).count()
    
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

    birthdate = serializers.CharField(required=False, allow_blank=True)
    checkbox = serializers.BooleanField(required=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError("La contraseña debe incluir tanto letras como números.")
        return value

    def validate_email(self, value):
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError("El correo debe ser una dirección de @gmail.com.")
        return value

    def validate_birthdate(self, value):
        if not value:
            raise serializers.ValidationError("Este campo no puede estar en blanco.")
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise serializers.ValidationError("Fecha con formato erróneo. Use el formato YYYY-MM-DD.")
        
        return value
    
    def validate_checkbox(self, value):
        if value is False:
            raise serializers.ValidationError("Debes aceptar los términos y condiciones.")
        return value

    def create(self, validated_data):
        checkbox = validated_data.pop('checkbox')
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
                'birthdate', 'country_id', 'is_active', 'is_staff', 'checkbox']
        extra_kwargs = {
            'password': {'write_only': True},
            'biography': {'required': False},
            'phone_number': {'required': False},
            'birthdate': {'required': False},
            'checkbox': {'required': True},
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
#-----------------------------------------------------------------------------------------------------
# Comentarios
#-----------------------------------------------------------------------------------------------------                 
class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, source='post')
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True, source='status')
    comment_id = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), write_only=True, source='comment', required=False, allow_null=True)
    file = FileSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    reactions = ReactionSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_id',
            'post_id',
            'user_id',
            'body',
            'status_id',
            'status',
            'file',
            'reactions',
            'replies_count',
            'reactions',
            'reactions_count',
            'reports_count',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def get_replies_count(self, obj):
        # Método para contar la cantidad de respuestas que no estén bloqueadas
        return obj.replies.exclude(status__name__iexact='bloqueado').count()
    
    def get_reactions_count(self, obj):
        # Método para contar la cantidad de reacciones
        return obj.reactions.count()

    def get_reports_count(self, obj):
        # Método para contar la cantidad de reportes
        return obj.reports.count()

    def to_representation(self, instance):
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        representation = super().to_representation(instance)

        # Verificar si el comentario tiene un comentario padre
        parent_comment_id = instance.comment.id if instance.comment else None

        return {
            'id': representation['id'],
            'attributes': {
                'body': representation['body'],
                'status_id': instance.status.id, 
                'post_id': instance.post.id,
                'user_id': instance.user.id,  
                'comment_id': parent_comment_id,  # Incluir el ID del comentario padre si existe
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
                'status': representation['status'],
                'file': representation['file'],
                'reactions': representation['reactions'],
                'replies_count': representation['replies_count'],
                'reactions': representation['reactions'],
                'reactions_count': representation['reactions_count'],
                'reports_count': representation['reports_count'],
            }
        }
#-----------------------------------------------------------------------------------------------------
# Publicación
#-----------------------------------------------------------------------------------------------------       
class PostSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True, source='status')
    type_post = TypePostSerializer(read_only=True)
    type_post_id = serializers.PrimaryKeyRelatedField(queryset=TypePost.objects.all(), write_only=True, source='type_post')
    files = FileSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField() 
    comments_count = serializers.SerializerMethodField()
    reposts_count = serializers.SerializerMethodField() 
    shares_count = serializers.SerializerMethodField()  
    total_shares_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 
                'body', 
                'post',
                'user_id', 
                'status_id',
                'status', 
                'type_post_id', 
                'type_post',
                'files',
                'reactions',
                'reactions_count',
                'comments_count', 
                'reposts_count',
                'shares_count',
                'total_shares_count',
                'reports_count',
                'created_at', 
                'updated_at', 
                'deleted_at', 
                ]
    
    def get_post(self, obj):
        # Método para incluir la información del post original
        if obj.post:  # Si este post es un repost, incluir el post original
            return PostSerializer(obj.post, context=self.context).data
        return None  # Si no es un repost, no incluir nada
    
    def get_reactions_count(self, obj):
        # Método para contar la cantidad de reacciones
        return obj.reactions.count()

    def get_comments_count(self, obj):
        # Método para contar la cantidad de comentarios que no estén bloqueados
        return obj.comments.exclude(status__name__iexact='bloqueado').count()

    def get_reposts_count(self, obj):
        # Método para contar la cantidad de reposts que no estén bloqueados
        return obj.reposts.exclude(status__name__iexact='bloqueado').count()

    def get_shares_count(self, obj):
        # Método para contar la cantidad de shares
        return Share.objects.filter(post=obj).count()

    def get_total_shares_count(self, obj):
        # Método para sumar la cantidad de reposts y shares
        return self.get_reposts_count(obj) + self.get_shares_count(obj)
    
    def get_reports_count(self, obj):
        return obj.reports.count()
            
    def to_representation(self, instance):
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        representation = super().to_representation(instance)
        
        original_post_id = instance.post.id if instance.post else None
        
        return {
            'id': representation['id'],
            'attributes': {
                'body': representation['body'],
                'post_id': original_post_id,
                'user_id': instance.user.id,
                'status_id': instance.status.id, 
                'type_post_id': instance.type_post.id, 
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'post': representation['post'],
                'user': user_representation,
                'status': representation['status'],
                'type_post': representation['type_post'],
                'files': representation['files'],
                'reactions': representation['reactions'],
                'reactions_count': representation['reactions_count'],
                'comments_count': representation['comments_count'], 
                'reposts_count': representation['reposts_count'],
                'shares_count': representation['shares_count'],
                'total_shares_count': representation['total_shares_count'],
                'reports_count': representation['reports_count'],
            }
        }
#-----------------------------------------------------------------------------------------------------
# Compartir
#-----------------------------------------------------------------------------------------------------              
class ShareSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    post = PostSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, source='post')

    class Meta:
        model = Share
        fields = [
            'id',
            'user_id',
            'post_id',
            'post',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'user_id': instance.user.id,
                'post_id': instance.post.id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
                'post': representation['post'],
            }
        }
#-----------------------------------------------------------------------------------------------------
# Historia
#-----------------------------------------------------------------------------------------------------     
class StorySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), write_only=True, source='status')
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False, allow_null=True, write_only=True, source='post')
    post = PostSerializer(read_only=True)
    file = FileSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 
                'content', 
                'archive',
                'user_id', 
                'status_id',
                'status', 
                'post_id',
                'post',
                'file',
                'reactions',
                'reactions_count',
                'reports_count',
                'created_at', 
                'updated_at', 
                'deleted_at', 
                ]
    
    def get_reactions_count(self, obj):
        return obj.reactions.count()
    
    def get_reports_count(self, obj):
        return obj.reports.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        post_id = instance.post.id if instance.post else None
        
        return {
            'id': representation['id'],
            'attributes': {
                'content': representation['content'],
                'archive': representation['archive'],
                'user_id': instance.user.id,
                'status_id': instance.status.id,
                'post_id': post_id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'status': representation['status'],
                'post': representation['post'],
                'file': representation['file'],
                'reactions': representation['reactions'],
                'reactions_count': representation['reactions_count'],
                'reports_count': representation['reports_count'],
            }
        }
        
class StoryViewSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    story_id = serializers.PrimaryKeyRelatedField(queryset=Story.objects.all(), write_only=True, source='story')
    
    class Meta:
        model = StoryView
        fields = ('id',
                'story_id',
                'user_id', 
                'created_at',
                'updated_at', 
                )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'story_id': instance.story.id,
                'user_id': instance.user.id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
    
#-----------------------------------------------------------------------------------------------------
# Simple serialser
#----------------------------------------------------------------------------------------------------- 
class CommentSimpleSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, source='post')
    comment_id = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), write_only=True, source='comment', required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'comment_id',
            'post_id',
            'user_id',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        user_representation = get_user_with_profile_photo(instance.user, self.context)
        representation = super().to_representation(instance)

        # Verificar si el comentario tiene un comentario padre
        parent_comment_id = instance.comment.id if instance.comment else None

        return {
            'id': representation['id'],
            'attributes': {
                'post_id': instance.post.id,
                'user_id': instance.user.id,  
                'comment_id': parent_comment_id,  # Incluir el ID del comentario padre si existe
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
        }
                
class ShareSimpleSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, source='post')

    class Meta:
        model = Share
        fields = [
            'id',
            'user_id',
            'post_id',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'id': representation['id'],
            'attributes': {
                'user_id': instance.user.id,
                'post_id': instance.post.id,
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            }
        }
    
#-----------------------------------------------------------------------------------------------------
# Notificacion
#----------------------------------------------------------------------------------------------------- 

class NotificationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user', allow_null=True)
    receiver_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='receiver_user', allow_null=True)

    class Meta:
        model = Notification
        fields = (
            'id',
            'user_id',
            'content_type',
            'object_id',
            'receiver_user_id',
            'message',
            'type',
            'is_read',
            'created_at',
            'updated_at'
        )

    def to_representation(self, instance):
        user_representation = get_user_with_profile_photo(instance.user, self.context) if instance.user else None
        receiver_user_representation = get_user_with_profile_photo(instance.receiver_user, self.context) if instance.receiver_user else None
        
        comment_representation = None
        reaction_representation = None
        share_representation = None

        # Obtener el nombre del modelo de content_object
        model_name = None
        try:
            content_type = instance.content_type
            if content_type:
                model_class = content_type.model_class()
                related_object = model_class.objects.filter(id=instance.object_id).first()
                model_name = model_class._meta.model_name if related_object else None
        except ContentType.DoesNotExist:
            model_name = None

        if isinstance(instance.content_object, Comment):
            comment_representation = CommentSimpleSerializer(instance.content_object).data
        elif isinstance(instance.content_object, Reaction):
            reaction_representation = ReactionSerializer(instance.content_object, context={'request': self.context['request']}).data
        elif isinstance(instance.content_object, Share):
            share_representation = ShareSimpleSerializer(instance.content_object).data
        
        representation = super().to_representation(instance)

        return {
            'id': representation['id'],
            'attributes': {
                'content_type': representation['content_type'],
                'model_name': model_name,
                'object_id': representation['object_id'],
                'user_id': instance.user.id if instance.user else None,
                'receiver_user_id': instance.receiver_user.id if instance.receiver_user else None,
                'message': representation['message'],
                'type': representation['type'],
                'is_read': representation['is_read'],
                'created_at': representation['created_at'],
                'updated_at': representation['updated_at'],
            },
            'relationships': {
                'user': user_representation,
                'receiver_user': receiver_user_representation,
                'comment': comment_representation,
                'reaction': reaction_representation,
                'share': share_representation
            }
        }




