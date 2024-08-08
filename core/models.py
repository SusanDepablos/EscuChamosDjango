from django.db import models
from simple_history.models import HistoricalRecords
from .mixins import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

#-----------------------------------------------------------------------------------------------------
# País 
#-----------------------------------------------------------------------------------------------------

class Country(TimestampedMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre')
    abbreviation = models.CharField(max_length=10, blank=True, null=True, verbose_name='Abreviación')
    dialing_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código Telefónico')
    
    class Meta:
        db_table = 'countries' 
        verbose_name = 'País'
        verbose_name_plural = 'Paises'

    def __str__(self):
        return self.name
    

#-----------------------------------------------------------------------------------------------------
# User Manager
#-----------------------------------------------------------------------------------------------------

class UserManager(BaseUserManager):
    def _create_user(self, username, email, name, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            username=username,
            email=email,
            name=name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, name, password=None, **extra_fields):
        return self._create_user(username, email, name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name, password=None, **extra_fields):
        user = self._create_user(username, email, name, password, True, True, **extra_fields)
        
        # Asignar el superusuario al grupo con ID 1
        admin_group = Group.objects.get(id=1)
        user.groups.add(admin_group)
        
        return user

#-----------------------------------------------------------------------------------------------------
# Usuario 
#-----------------------------------------------------------------------------------------------------

class User(TimestampedMixin, SoftDeleteMixin, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name='Usuario')
    name = models.CharField(max_length=255, verbose_name='Nombre y Apellido')
    biography = models.TextField(blank=True, null=True, verbose_name='Biografía')
    password = models.CharField(max_length=255, verbose_name='Contraseña')
    email = models.EmailField(max_length=255, unique=True, verbose_name='Correo Electrónico')
    is_email_verified = models.BooleanField(default=False, verbose_name='El correo está verificado')
    verification_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Código de verificación')
    phone_number = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name='Número de teléfono')
    birthdate = models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento') 
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True, related_name='users', verbose_name='País')
    is_active = models.BooleanField(default=True, verbose_name='¿Está Activo?')
    is_staff = models.BooleanField(default=False, verbose_name='¿Es Admin?')
    historical = HistoricalRecords()
    objects = UserManager()
    
    files = GenericRelation('File')
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']
    
    class Meta:
        db_table = 'users' 
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.name
    
#-----------------------------------------------------------------------------------------------------
# Archivo 
#-----------------------------------------------------------------------------------------------------
class File(TimestampedMixin, SoftDeleteMixin, models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Tipo de contenido')
    object_id = models.PositiveIntegerField(verbose_name='ID del objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    path = models.CharField(max_length=255, verbose_name='Ruta')
    extension = models.CharField(max_length=10, verbose_name='Extensión')
    size = models.CharField(max_length=20, verbose_name='Tamaño')
    type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tipo')
    
    class Meta:
        db_table = 'files'
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        
    def __str__(self):
        return self.path
    
#-----------------------------------------------------------------------------------------------------
# Seguimiento
#-----------------------------------------------------------------------------------------------------
class Follow(TimestampedMixin, models.Model):
    following_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE, verbose_name='Usuario que sigue')
    followed_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE, verbose_name='Usuario seguido')

    class Meta:
        db_table = 'follows'
        unique_together = ('following_user', 'followed_user')
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'

    def __str__(self):
        return f"{self.following_user} sigue a {self.followed_user}"
    
#-----------------------------------------------------------------------------------------------------
# Estado
#-----------------------------------------------------------------------------------------------------

class Status(TimestampedMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    
    class Meta:
        db_table = 'statuses' 
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.name

#-----------------------------------------------------------------------------------------------------
# Reacción 
#-----------------------------------------------------------------------------------------------------
class Reaction(TimestampedMixin, models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Tipo de contenido')
    object_id = models.PositiveIntegerField(verbose_name='ID del objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', related_name='reactions')

    class Meta:
        db_table = 'reactions'
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'

    def __str__(self):
        return f'{self.user.username} reaccionó a {self.content_type} con ID {self.object_id}'
    
#-----------------------------------------------------------------------------------------------------
# Tipo de publicación
#-----------------------------------------------------------------------------------------------------

class TypePost(TimestampedMixin, SoftDeleteMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    
    class Meta:
        db_table = 'type_posts' 
        verbose_name = 'Tipo de publicación'
        verbose_name_plural = 'Tipo de publicaciones'

    def __str__(self):
        return self.name
    
#-----------------------------------------------------------------------------------------------------
# Reporte 
#-----------------------------------------------------------------------------------------------------
class Report(TimestampedMixin, models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Tipo de contenido')
    object_id = models.PositiveIntegerField(verbose_name='ID del objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', related_name='reports')
    observation = models.TextField(verbose_name='Observación')

    class Meta:
        db_table = 'reports'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'

    def __str__(self):
        return f'{self.user.username} reporto a {self.content_type} con ID {self.object_id}'
    
#-----------------------------------------------------------------------------------------------------
# Publicación
#-----------------------------------------------------------------------------------------------------
class Post(TimestampedMixin, SoftDeleteMixin, models.Model):
    body = models.TextField(null=True, blank=True, verbose_name='Cuerpo')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', related_name='posts')
    type_post = models.ForeignKey(TypePost, on_delete=models.PROTECT, verbose_name='Tipo de Publicación', related_name='posts')
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Estado', related_name='post')
    post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='reposts', verbose_name='Publicación Padre')

    files = GenericRelation(File)
    reports = GenericRelation(Report)
    reactions = GenericRelation(Reaction)
    
    class Meta:
        db_table = 'posts'
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        
    def __str__(self):
        return self.body
#-----------------------------------------------------------------------------------------------------
# Compartir
#-----------------------------------------------------------------------------------------------------
class Share(TimestampedMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Publicación', related_name='shares')

    class Meta:
        db_table = 'shares'
        verbose_name = 'Compartir'
        verbose_name_plural = 'Compartir'

    def __str__(self):
        return f'{self.user} compartió {self.post}'