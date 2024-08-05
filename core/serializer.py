from rest_framework import serializers
from django.contrib.auth.models import *
from .models import *
from django.contrib.auth.hashers import make_password

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
        
class UserSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), write_only=True, allow_null=True, source='country')
    groups = GroupSerializer(many=True, read_only=True)
    
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
                'groups'
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
                'groups': representation['groups'] 
            }
        }
        
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