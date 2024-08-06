from django.core.management.base import BaseCommand
from core.models import *
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Sembrar datos en modelos de la aplicación'

    def handle(self, *args, **options):
        self.seed_groups()
        self.seed_countries()
        self.seed_statuses()
        
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
            {'name': 'Antigua and Barbuda', 'abbreviation': 'ATG', 'dialing_code': '+1-268'},
            {'name': 'Argentina', 'abbreviation': 'ARG', 'dialing_code': '+54'},
            {'name': 'Bahamas', 'abbreviation': 'BHS', 'dialing_code': '+1-242'},
            {'name': 'Barbados', 'abbreviation': 'BRB', 'dialing_code': '+1-246'},
            {'name': 'Belice', 'abbreviation': 'BLZ', 'dialing_code': '+501'},
            {'name': 'Bolivia', 'abbreviation': 'BOL', 'dialing_code': '+591'},
            {'name': 'Brasil', 'abbreviation': 'BRA', 'dialing_code': '+55'},
            {'name': 'Canadá', 'abbreviation': 'CAN', 'dialing_code': '+1'},
            {'name': 'Chile', 'abbreviation': 'CHL', 'dialing_code': '+56'},
            {'name': 'Colombia', 'abbreviation': 'COL', 'dialing_code': '+57'},
            {'name': 'Costa Rica', 'abbreviation': 'CRI', 'dialing_code': '+506'},
            {'name': 'Cuba', 'abbreviation': 'CUB', 'dialing_code': '+53'},
            {'name': 'Dominica', 'abbreviation': 'DMA', 'dialing_code': '+1-767'},
            {'name': 'República Dominicana', 'abbreviation': 'DOM', 'dialing_code': '+1-809'},
            {'name': 'Ecuador', 'abbreviation': 'ECU', 'dialing_code': '+593'},
            {'name': 'El Salvador', 'abbreviation': 'SLV', 'dialing_code': '+503'},
            {'name': 'Granada', 'abbreviation': 'GRD', 'dialing_code': '+1-473'},
            {'name': 'Guatemala', 'abbreviation': 'GTM', 'dialing_code': '+502'},
            {'name': 'Guyana', 'abbreviation': 'GUY', 'dialing_code': '+592'},
            {'name': 'Haití', 'abbreviation': 'HTI', 'dialing_code': '+509'},
            {'name': 'Honduras', 'abbreviation': 'HND', 'dialing_code': '+504'},
            {'name': 'Jamaica', 'abbreviation': 'JAM', 'dialing_code': '+1-876'},
            {'name': 'México', 'abbreviation': 'MEX', 'dialing_code': '+52'},
            {'name': 'Nicaragua', 'abbreviation': 'NIC', 'dialing_code': '+505'},
            {'name': 'Panamá', 'abbreviation': 'PAN', 'dialing_code': '+507'},
            {'name': 'Paraguay', 'abbreviation': 'PRY', 'dialing_code': '+595'},
            {'name': 'Perú', 'abbreviation': 'PER', 'dialing_code': '+51'},
            {'name': 'San Cristóbal y Nieves', 'abbreviation': 'KNA', 'dialing_code': '+1-869'},
            {'name': 'Santa Lucía', 'abbreviation': 'LCA', 'dialing_code': '+1-758'},
            {'name': 'San Vicente y las Granadinas', 'abbreviation': 'VCT', 'dialing_code': '+1-784'},
            {'name': 'Surinam', 'abbreviation': 'SUR', 'dialing_code': '+597'},
            {'name': 'Trinidad y Tobago', 'abbreviation': 'TTO', 'dialing_code': '+1-868'},
            {'name': 'Estados Unidos', 'abbreviation': 'USA', 'dialing_code': '+1'},
            {'name': 'Uruguay', 'abbreviation': 'URY', 'dialing_code': '+598'},
            {'name': 'Venezuela', 'abbreviation': 'VEN', 'dialing_code': '+58'},
        ]
        for country_data in countries:
            Country.objects.get_or_create(**country_data)

    def seed_statuses(self):
        statuses = [
            ('Activo', 'Estado normal sin infracciones'),
            ('Infracción', 'Estado de infracción por violación de reglas'),
            ('En revisión', 'Estado de revisión pendiente'),
            ('Resuelto', 'Estado de infracción resuelto'),
            ('Bloqueado', 'Estado de contenido bloqueado'),
            ('Reportado', 'Estado de contenido reportado'),
        ]
        for name, description in statuses:
            Status.objects.get_or_create(name=name, description=description)