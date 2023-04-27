from django.forms import ModelForm, TimeInput, DateInput
from .models import Task, Commission, Register_assistence, Vacation_rescheduling, \
                    Official_permit_for_hours, Personal_leave_with_pay, Vacation_account_request, Data_user

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['reason', 'detail','startdate','finaldate']

class CommissionForm(ModelForm):
    class Meta:
        model = Commission
        fields = ['unit', 'detail','startdate','finaldate']
class Register_assistenceForm(ModelForm):
    class Meta:
        model = Register_assistence
        fields = ['date', 'hora_ingreso_mañana','hora_salida_mañana','hora_ingreso_tarde','hora_salida_tarde','reason','constancy']
        widgets = {'date': DateInput(attrs={'type': 'date', 'required': True}),
                   'hora_ingreso_mañana': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'hora_salida_mañana': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'hora_ingreso_tarde': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'hora_salida_tarde': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False})}

class Vacation_reschedulingForm(ModelForm):
    class Meta:
        model = Vacation_rescheduling
        fields = ['fecha_programada1_desde', 'fecha_programada1_hasta', 'fecha_programada2_desde',
                  'fecha_programada2_hasta','fecha_de_reprogramación1_desde','fecha_de_reprogramación1_hasta',
                  'fecha_de_reprogramación2_desde','fecha_de_reprogramación2_hasta',
                  'fecha_de_reprogramación3_desde','fecha_de_reprogramación3_hasta',
                  'motivos_de_reprogramación','justificación_de_la_reprogramación','dias_habiles']
class Official_permit_for_hoursForm(ModelForm):
    class Meta:
        model = Official_permit_for_hours
        fields = ['comisión','motivo_de_la_comisión','fecha_de_salida','desde_hora_m','hasta_hora_m','desde_hora_t','hasta_hora_t']
        widgets = {'desde_hora_m': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'hasta_hora_m': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'desde_hora_t': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False}),
                   'hasta_hora_t': TimeInput(format='%H:%M', attrs={'type': 'time', 'step': 1, 'required': False})}

class Personal_leave_with_payForm(ModelForm):
    class Meta:
        model = Personal_leave_with_pay
        fields = ['compensación','fecha_de_compensación','compensación_desde_hora','compensación_hasta_hora'
                ,'fecha_de_salida','salida_desde_hora','salida_hasta_hora']

class Vacation_account_requestForm(ModelForm):
    class Meta:
        model = Vacation_account_request
        fields = ['fecha_de_solicitud','fecha_solicitada1','fecha_solicitada1_hasta',
                  'fecha_solicitada2','fecha_solicitada2_hasta','fecha_solicitada3','fecha_solicitada3_hasta',
                  'motivo','justificación']
class Data_userForm(ModelForm):
    class Meta:
        model = Data_user
        fields = ['nombre','a_paterno','a_materno','reparticion','item','fecha_de_ingreso','dias_de_vacacion']