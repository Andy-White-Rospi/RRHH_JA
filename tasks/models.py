from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from datetime import time, date
# Create your models here.
# Crear grupos
User = get_user_model()

# content_type = ContentType.objects.get(app_label='app_name', model='model_name')
permission = Permission.objects.get(codename='view_vacation_rescheduling')

group1, created = Group.objects.get_or_create(name='Funcionarios')
group2, created = Group.objects.get_or_create(name='F_RRHH')
group2.permissions.add(permission)

class Task(models.Model):
    reason = models.CharField(max_length=200)
    detail = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    finaldate = models.DateTimeField(null=True, blank=True)
    startdate = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Commission(models.Model):
    reason = models.CharField(max_length=200)
    unit = models.CharField(max_length=200)
    detail = models.TextField(max_length=1000)
    finaldate = models.DateTimeField(null=True, blank=True)
    startdate = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Register_assistence(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    hora_ingreso_mañana = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    hora_salida_mañana = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    hora_ingreso_tarde = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    hora_salida_tarde = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    reason = models.CharField(max_length=200, null=True, blank=True)
    aprobacion = models.BooleanField(default=False, null=True, blank=True)
    constancy = models.CharField(max_length=200, null=True, blank=True)
    dateapproved = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Vacation_rescheduling(models.Model):
    fecha_programada1_desde = models.DateTimeField(null=True, blank=True)
    fecha_programada1_hasta = models.DateTimeField(null=True, blank=True)
    fecha_programada2_desde = models.DateTimeField(null=True, blank=True)
    fecha_programada2_hasta = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación1_desde = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación1_hasta = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación2_desde = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación2_hasta = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación3_desde = models.DateTimeField(null=True, blank=True)
    fecha_de_reprogramación3_hasta = models.DateTimeField(null=True, blank=True)
    motivos_de_reprogramación = models.CharField(max_length=200, null=True, blank=True)
    dias_habiles = models.IntegerField(null=True, blank=True)
    justificación_de_la_reprogramación = models.CharField(max_length=500, null=True, blank=True)
    aprobacion = models.BooleanField(default=False, null=True, blank=True)
    dateapproved = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Official_permit_for_hours(models.Model):
    comisión = models.CharField(max_length=200, null=True, blank=True)
    motivo_de_la_comisión = models.CharField(max_length=500, null=True, blank=True)
    fecha_de_salida = models.DateTimeField(null=True, blank=True)
    desde_hora_m = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    hasta_hora_m = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    desde_hora_t = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    hasta_hora_t = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    aprobacion = models.BooleanField(default=False, null=True, blank=True)
    dateapproved = models.DateTimeField(null=True, blank=True)
    horas_de_permiso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Personal_leave_with_pay(models.Model):
  compensación = models.CharField(max_length=200,null=True, blank=True)
  fecha_de_compensación = models.DateTimeField(null=True, blank=True)
  compensación_desde_hora = models.TimeField(verbose_name='Hora del día',null=True, blank=True)
  compensación_hasta_hora = models.TimeField(verbose_name='Hora del día',null=True, blank=True)
  fecha_de_salida = models.DateTimeField(null=True, blank=True)
  salida_desde_hora_m = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
  salida_hasta_hora_m = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
  salida_desde_hora_t = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
  salida_hasta_hora_t = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
  aprobacion = models.BooleanField(default=False,null=True, blank=True)
  dateapproved = models.DateTimeField(null=True, blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class Vacation_account_request(models.Model):
  fecha_de_solicitud = models.DateTimeField(null=True, blank=True)
  fecha_solicitada1 = models.DateTimeField(null=True, blank=True)
  fecha_solicitada1_hasta = models.DateTimeField(null=True, blank=True)
  fecha_solicitada2 = models.DateTimeField(null=True, blank=True)
  fecha_solicitada2_hasta = models.DateTimeField(null=True, blank=True)
  fecha_solicitada3 = models.DateTimeField(null=True, blank=True)
  fecha_solicitada3_hasta = models.DateTimeField(null=True, blank=True)
  dias_habiles_programados = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
  justificación = models.CharField(max_length=1000,null=True, blank=True)
  aprobacion = models.BooleanField(default=False,null=True, blank=True)
  dateapproved = models.DateTimeField(null=True, blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class Data_user(models.Model):
  nombre = models.CharField(max_length=25,null=True, blank=True)
  a_paterno = models.CharField(max_length=15,null=True, blank=True)
  a_materno = models.CharField(max_length=15,null=True, blank=True)
  reparticion = models.CharField(max_length=10,null=True, blank=True)
  item = models.IntegerField(null=True, blank=True)
  fecha_de_ingreso = models.DateTimeField(null=True, blank=True)
  dias_de_vacacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
  fecha_en_que_se_asigno_vacacion = models.DateTimeField(null=False, blank=False, default=date(2000,1,1))
  fecha_en_que_se_asigno_dias_goce = models.DateTimeField(null=False, blank=False, default=date(2000,1,1))
  horas_con_goce_de_haberes = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

class Horas_laborales(models.Model):
    ingreso_mañana = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    salida_mañana = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    ingreso_tarde = models.TimeField(verbose_name='Hora del día', null=True, blank=True)
    salida_tarde = models.TimeField(verbose_name='Hora del día', null=True, blank=True)

    def __str__(self):
        return self.reason + ' - ' + self.user.username

# ingreso_mañana = time(8,00)
# salida_mañana = time(12,00)
# ingreso_tarde = time(14,30)
# salida_tarde = time(18,30)
#
# horas_laborales =Horas_laborales.objects.create(ingreso_mañana=ingreso_mañana,salida_mañana=salida_mañana,ingreso_tarde=ingreso_tarde,salida_tarde=salida_tarde)
