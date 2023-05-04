# Generated by Django 4.1 on 2023-04-27 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_official_permit_for_hours_horas_asignadas'),
    ]

    operations = [
        migrations.RenameField(
            model_name='official_permit_for_hours',
            old_name='desde_hora',
            new_name='desde_hora_m',
        ),
        migrations.RenameField(
            model_name='official_permit_for_hours',
            old_name='hasta_hora',
            new_name='desde_hora_t',
        ),
        migrations.AddField(
            model_name='official_permit_for_hours',
            name='hasta_hora_m',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora del día'),
        ),
        migrations.AddField(
            model_name='official_permit_for_hours',
            name='hasta_hora_t',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora del día'),
        ),
    ]
