from django.core.management.base import BaseCommand
from core.models import *
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Sembrar datos en modelos de la aplicación'

    def handle(self, *args, **options):
        self.seed_groups()
        self.seed_countries()
        self.seed_statuses()
        self.seed_type_post()
        
    def seed_groups(self):
        groups = [
            ('Administrador'),
            ('Voluntario'),
            ('Usuario Normal'),
        ]
        for name in groups:
            Group.objects.get_or_create(name=name)

    def seed_countries(self):
        countries = [
            {'name': 'Antigua and Barbuda', 'abbreviation': 'ATG', 'dialing_code': '+1-268', 'iso': 'AG'},
            {'name': 'Argentina', 'abbreviation': 'ARG', 'dialing_code': '+54', 'iso': 'AR'},
            {'name': 'Bahamas', 'abbreviation': 'BHS', 'dialing_code': '+1-242', 'iso': 'BS'},
            {'name': 'Barbados', 'abbreviation': 'BRB', 'dialing_code': '+1-246', 'iso': 'BB'},
            {'name': 'Belice', 'abbreviation': 'BLZ', 'dialing_code': '+501', 'iso': 'BZ'},
            {'name': 'Bolivia', 'abbreviation': 'BOL', 'dialing_code': '+591', 'iso': 'BO'},
            {'name': 'Brasil', 'abbreviation': 'BRA', 'dialing_code': '+55', 'iso': 'BR'},
            {'name': 'Canadá', 'abbreviation': 'CAN', 'dialing_code': '+1', 'iso': 'CA'},
            {'name': 'Chile', 'abbreviation': 'CHL', 'dialing_code': '+56', 'iso': 'CL'},
            {'name': 'Colombia', 'abbreviation': 'COL', 'dialing_code': '+57', 'iso': 'CO'},
            {'name': 'Costa Rica', 'abbreviation': 'CRI', 'dialing_code': '+506', 'iso': 'CR'},
            {'name': 'Cuba', 'abbreviation': 'CUB', 'dialing_code': '+53', 'iso': 'CU'},
            {'name': 'Dominica', 'abbreviation': 'DMA', 'dialing_code': '+1-767', 'iso': 'DM'},
            {'name': 'República Dominicana', 'abbreviation': 'DOM', 'dialing_code': '+1-809', 'iso': 'DO'},
            {'name': 'Ecuador', 'abbreviation': 'ECU', 'dialing_code': '+593', 'iso': 'EC'},
            {'name': 'El Salvador', 'abbreviation': 'SLV', 'dialing_code': '+503', 'iso': 'SV'},
            {'name': 'Granada', 'abbreviation': 'GRD', 'dialing_code': '+1-473', 'iso': 'GD'},
            {'name': 'Guatemala', 'abbreviation': 'GTM', 'dialing_code': '+502', 'iso': 'GT'},
            {'name': 'Guyana', 'abbreviation': 'GUY', 'dialing_code': '+592', 'iso': 'GY'},
            {'name': 'Haití', 'abbreviation': 'HTI', 'dialing_code': '+509', 'iso': 'HT'},
            {'name': 'Honduras', 'abbreviation': 'HND', 'dialing_code': '+504', 'iso': 'HN'},
            {'name': 'Jamaica', 'abbreviation': 'JAM', 'dialing_code': '+1-876', 'iso': 'JM'},
            {'name': 'México', 'abbreviation': 'MEX', 'dialing_code': '+52', 'iso': 'MX'},
            {'name': 'Nicaragua', 'abbreviation': 'NIC', 'dialing_code': '+505', 'iso': 'NI'},
            {'name': 'Panamá', 'abbreviation': 'PAN', 'dialing_code': '+507', 'iso': 'PA'},
            {'name': 'Paraguay', 'abbreviation': 'PRY', 'dialing_code': '+595', 'iso': 'PY'},
            {'name': 'Perú', 'abbreviation': 'PER', 'dialing_code': '+51', 'iso': 'PE'},
            {'name': 'San Cristóbal y Nieves', 'abbreviation': 'KNA', 'dialing_code': '+1-869', 'iso': 'KN'},
            {'name': 'Santa Lucía', 'abbreviation': 'LCA', 'dialing_code': '+1-758', 'iso': 'LC'},
            {'name': 'San Vicente y las Granadinas', 'abbreviation': 'VCT', 'dialing_code': '+1-784', 'iso': 'VC'},
            {'name': 'Surinam', 'abbreviation': 'SUR', 'dialing_code': '+597', 'iso': 'SR'},
            {'name': 'Trinidad y Tobago', 'abbreviation': 'TTO', 'dialing_code': '+1-868', 'iso': 'TT'},
            {'name': 'Estados Unidos', 'abbreviation': 'USA', 'dialing_code': '+1', 'iso': 'US'},
            {'name': 'Uruguay', 'abbreviation': 'URY', 'dialing_code': '+598', 'iso': 'UY'},
            {'name': 'Venezuela', 'abbreviation': 'VEN', 'dialing_code': '+58', 'iso': 'VE'},
        ]
        
        for country_data in countries:
            Country.objects.update_or_create(
                abbreviation=country_data['abbreviation'],
                defaults=country_data
            )

    def seed_statuses(self):
        statuses = [
            ('Activo', 'Estado normal sin infracciones'),
            ('Reportado', 'Estado de contenido reportado'),
            ('Resuelto', 'Estado de infracción resuelto'),
            ('Bloqueado', 'Estado de contenido bloqueado'),
        ]
        for name, description in statuses:
            Status.objects.get_or_create(name=name, description=description)
            
    def seed_type_post(self):
        type_posts = [
            ('Normal', 'Publicación normal de texto'),
            ('Multimedia', 'Publicación que contiene imágenes, videos o audios'),
            ('Republicado', 'Publicación Republicada'),
            ('Escuchamos', 'Publicación donde los voluntarios y administradores pueden interactuar con la comunidad')
        ]
        for name, description in type_posts:
            TypePost.objects.get_or_create(name=name, description=description)
            
            
