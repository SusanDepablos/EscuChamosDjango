# Generated by Django 5.0.7 on 2024-08-06 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Borrado')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Estado',
                'verbose_name_plural': 'Estados',
                'db_table': 'statuses',
            },
        ),
    ]
