# Generated by Django 4.1 on 2023-04-27 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_alter_data_user_dias_de_vacacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='official_permit_for_hours',
            name='horas_asignadas',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]