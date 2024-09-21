from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import math
import uuid
from PIL import Image, ExifTags
from moviepy.editor import VideoFileClip

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
        
        # Generar un nombre único para el archivo basado en UUID
        file_extension = uploaded_file.name.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(media_root, destination_path, unique_filename)
        
        # Asegurarse de que el directorio de destino exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Verificar el tipo de archivo para aplicar compresión adecuada
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            self.compress_image(uploaded_file, file_path, file_extension)
        elif file_extension in ['mp4', 'avi', 'mov', 'webm']:
            self.compress_video(uploaded_file, file_path)
        else:
            # Guardar el archivo sin compresión si no es imagen ni video
            self.save_file(uploaded_file, file_path)

        # Obtener el tamaño del archivo comprimido
        compressed_file_size = os.path.getsize(file_path)
        
        return file_path, compressed_file_size

    def save_file(self, uploaded_file, file_path):
        # Guardar el archivo sin compresión
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    def compress_image(self, uploaded_file, file_path, file_extension):
        # Abrir la imagen usando Pillow
        image = Image.open(uploaded_file)
        
        # Corregir orientación basada en EXIF (si está disponible)
        image = self.correct_image_orientation(image)
        
        # Convertir a RGB si es necesario
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Comprimir la imagen y guardarla
        if file_extension in ['jpg', 'jpeg']:
            image.save(file_path, 'JPEG', quality=75, optimize=True)
        elif file_extension == 'png':
            image.save(file_path, 'PNG', optimize=True)

    def correct_image_orientation(self, image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif:
                orientation = exif.get(orientation, None)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass  # Ignorar si no hay EXIF o algo falla
        return image

    def compress_video(self, uploaded_file, file_path):
        # Utilizar moviepy para comprimir el video
        with VideoFileClip(uploaded_file.temporary_file_path()) as video:
            # Reducir la calidad de video manteniendo el tamaño original
            video.write_videofile(file_path, bitrate="500k")  # Ajusta el bitrate según necesidad

    def put_file(self, uploaded_file, destination_path='', file_type=''):
        destination_path = destination_path if destination_path else ''
        file_path, compressed_file_size = self.store_file(destination_path, uploaded_file)

        file_extension = uploaded_file.name.split('.')[-1]

        # Usar el tamaño del archivo comprimido
        file_size = self.convert_size(compressed_file_size)

        return {
            'path': file_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),  # Limpiar el path
            'extension': file_extension,
            'size': file_size,  # Nuevo tamaño del archivo comprimido
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