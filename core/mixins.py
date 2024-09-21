from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import math
import uuid

#-----------------------------------------------------------------------------------------------------
# Fecha de creado y fecha de actualizado
#-----------------------------------------------------------------------------------------------------
class TimestampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        
#-----------------------------------------------------------------------------------------------------
# Borrado suave
#-----------------------------------------------------------------------------------------------------
class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Borrado')

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
#-----------------------------------------------------------------------------------------------------
# Subir y eliminar archivos
#-----------------------------------------------------------------------------------------------------
class FileUploadMixin:
    def store_file(self, destination_path, uploaded_file):
        media_root = settings.MEDIA_ROOT
        
        # Generar un nombre único para el archivo basado solo en UUID
        file_extension = uploaded_file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(media_root, destination_path, unique_filename)
        
        # Asegurarse de que el directorio de destino exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar el archivo
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        return os.path.normpath(os.path.join(destination_path, unique_filename)).replace('\\', '/')
    def put_file(self, uploaded_file, destination_path='', file_type=''):
        destination_path = destination_path if destination_path else ''
        path = self.store_file(destination_path, uploaded_file)

        file_extension = uploaded_file.name.split('.')[-1]
        file_size = self.convert_size(uploaded_file.size)

        return {
            'path': path,
            'extension': file_extension,
            'size': file_size,
            'type': file_type,
        }
        
    def delete_file(self, file_path):
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"