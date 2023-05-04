from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from .models import Task,Vacation_rescheduling, Commission, Register_assistence, \
    Official_permit_for_hours, Personal_leave_with_pay, Vacation_account_request, Data_user, Horas_laborales
from datetime import time,datetime, date
from dateutil.relativedelta import relativedelta
from .forms import TaskForm, CommissionForm,Register_assistenceForm, Vacation_reschedulingForm,\
            Official_permit_for_hoursForm, Personal_leave_with_payForm, Vacation_account_requestForm,\
            Data_userForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


# Create your views here.
group1= Group.objects.get(name='Funcionarios')
group2= Group.objects.get(name='F_RRHH')

def tiempo_de_trabajo(usuario):
    data_usuario = Data_user.objects.get(id=usuario)
    fecha_registro = data_usuario.fecha_de_ingreso
    fecha_actual = timezone.now()
    # fecha_registro = Data_user.fecha_de_ingreso()
    fecha_actual_dt = datetime.strptime(str(fecha_actual), '%Y-%m-%d %H:%M:%S.%f%z')
    fecha_registro_dt = datetime.strptime(str(fecha_registro), '%Y-%m-%d %H:%M:%S%z')
    diferencia = relativedelta(fecha_actual_dt, fecha_registro_dt)
    anios_de_trabajo = int(diferencia.years)
    return anios_de_trabajo

def asignar_hora_con_goce(usuario):
    data_usuario = Data_user.objects.get(id=usuario)
    fecha_asignacion = data_usuario.fecha_en_que_se_asigno_dias_goce
    fecha_actual = timezone.now()
    año_actual=fecha_actual.year
    mes_actual=fecha_actual.month
    mes = fecha_asignacion.month  # Extrae el mes de la fecha
    dif_mes = mes_actual - mes
    if ((dif_mes>0)|(dif_mes==-11)):
        data_usuario.horas_con_goce_de_haberes = 0
        nueva_asignacion = date(año_actual,mes_actual,1)
        data_usuario.fecha_en_que_se_asigno_dias_goce = nueva_asignacion
        data_usuario.save()

def asignar_vacaciones(usuario):
    data_usuario = Data_user.objects.get(id=usuario)
    fecha_registro = data_usuario.fecha_de_ingreso
    fecha_asignacion = data_usuario.fecha_en_que_se_asigno_vacacion
    fecha_actual = timezone.now()
    fecha_actual_dt = datetime.strptime(str(fecha_actual), '%Y-%m-%d %H:%M:%S.%f%z')
    fecha_asignacion_dt = datetime.strptime(str(fecha_asignacion), '%Y-%m-%d %H:%M:%S%z')
    diferencia = relativedelta(fecha_actual_dt, fecha_asignacion_dt)
    anios = int(diferencia.years)
    mes_registro=fecha_registro.month
    dia_registro=fecha_registro.day
    año_actual=fecha_actual.year
    mes_actual=fecha_actual.month
    dia_actual=fecha_actual.day
    años = fecha_asignacion.year
    mes = fecha_asignacion.month  # Extrae el mes de la fecha
    dia = fecha_asignacion.day  # Extrae el día de la fecha
    dif_mes = mes_actual - mes
    dif_dia = dia_actual - dia
    if ((anios>=1)&(dif_mes>=0)&(dif_dia>=0)):
        if ( (2000==años)&(1==mes)&(1==dia) ):
            if ( mes_actual>mes):
                nueva_asignacion = date(año_actual,mes_registro,dia_registro)
                data_usuario.fecha_en_que_se_asigno_vacacion = nueva_asignacion
                data_usuario.save()
        else:
            anios_de_trabajo = tiempo_de_trabajo(usuario)
            if (anios_de_trabajo < 1):
                dias_de_vacaciones = 0
            elif (1 <= anios_de_trabajo < 5):
                dias_de_vacaciones = 15
            elif (5 <= anios_de_trabajo < 10):
                dias_de_vacaciones = 20
            elif (10 <= anios_de_trabajo):
                dias_de_vacaciones = 30
            else:
                dias_de_vacaciones=0
            vacacion_acumulada = data_usuario.dias_de_vacacion
            data_usuario.dias_de_vacacion = (vacacion_acumulada+dias_de_vacaciones)
            nueva_asignacion = date(año_actual,mes_registro,dia_registro)
            data_usuario.fecha_en_que_se_asigno_vacacion = nueva_asignacion
            data_usuario.save()

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)

                group1.user_set.add(user)
                form = Data_userForm(request.POST)
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})

def signupRRHH(request):
    if request.method == 'GET':
        return render(request, 'signup_RRHH.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)

                group2.user_set.add(user)
                print(group2)
                form = Data_userForm(request.POST)
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('approve')
            except IntegrityError:
                return render(request, 'signup_RRHH.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'signup_RRHH.html', {"form": UserCreationForm, "error": "Passwords did not match."})

@login_required
@permission_required('tasks.view_vacation_rescheduling')
def approve(request):
    usuarios = Vacation_rescheduling.objects.filter(aprobacion=False).values_list('id','user__username')
    usuarios1 = Vacation_account_request.objects.filter(aprobacion=False).values_list('id','user__username')
    usuarios2 = Register_assistence.objects.filter(aprobacion=False).values_list('id','user__username')
    usuarios3 = Personal_leave_with_pay.objects.filter(aprobacion=False).values_list('id','user__username')
    usuarios4 = Official_permit_for_hours.objects.filter(aprobacion=False).values_list('id','user__username')
    usuario = request.user.id
    data_usuario = Data_user.objects.get(user_id=usuario)
    id_data_user = data_usuario.id
    asignar_vacaciones(id_data_user)
    return render(request,'approve.html', {"usuarios":usuarios,"usuarios1":usuarios1,"usuarios2":usuarios2,"usuarios3":usuarios3,"usuarios4":usuarios4})

@login_required
def tasks(request):
    tasks = Vacation_rescheduling.objects.filter(user=request.user)
    tasks1 = Vacation_account_request.objects.filter(user=request.user)
    tasks2 = Register_assistence.objects.filter(user=request.user)
    tasks3 = Personal_leave_with_pay.objects.filter(user=request.user)
    tasks4 = Official_permit_for_hours.objects.filter(user=request.user)
    usuario = request.user.id
    data_usuario = Data_user.objects.get(user_id=usuario)
    id_data_user = data_usuario.id
    asignar_vacaciones(id_data_user)
    return render(request, 'tasks.html', {"tasks": tasks,"tasks1": tasks1,"tasks2": tasks2,"tasks3": tasks3,"tasks4": tasks4})

@login_required
def commission(request):
    if request.method == "GET":
        return render(request,'commission.html',{"form": CommissionForm})
    else:
        try:
            form = CommissionForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'commission.html',
                          {"form": TaskForm, "error": "Error creating task." + new_task + "Hola"})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
def registro_de_asistencia(request):
    if request.method == "GET":
        return render(request, 'register_of_assistence.html', {"form": Register_assistenceForm})
    else:
        try:
            form = Register_assistenceForm(request.POST)
            if form.is_valid():
                fecha = form.cleaned_data['date']
                desde_hora_m = form.cleaned_data['hora_ingreso_mañana']
                hasta_hora_m = form.cleaned_data['hora_salida_mañana']
                desde_hora_t = form.cleaned_data['hora_ingreso_tarde']
                hasta_hora_t = form.cleaned_data['hora_salida_tarde']
                fecha_actual = timezone.now()
                if(fecha>fecha_actual):
                    return render(request, 'register_of_assistence.html',
                                  {"form": Register_assistenceForm, "error": "La fecha no puede ser posterior al día de hoy"})
                if desde_hora_m is None:
                    if hasta_hora_m is None:
                        if desde_hora_t is None:
                            if hasta_hora_t is None:
                                return render(request, 'register_of_assistence.html',
                                              {"form": Register_assistenceForm, "error": "Ningun horario introducido"})
                else:
                    query = Q(ingreso_mañana__lte=desde_hora_m) & Q(salida_mañana__gte=desde_hora_m)
                    horario_valido = Horas_laborales.objects.filter(query).exists()
                    if horario_valido==False:
                        return render(request, 'register_of_assistence.html',
                                      {"form": Register_assistenceForm, "error": "Fuera del horario de la mañana"})
                if hasta_hora_m is not None:
                    query = Q(ingreso_mañana__lte=hasta_hora_m) & Q(salida_mañana__gte=hasta_hora_m)
                    horario_valido = Horas_laborales.objects.filter(query).exists()
                    if horario_valido==False:
                        return render(request, 'register_of_assistence.html',
                                      {"form": Register_assistenceForm, "error": "Fuera del horario de la mañana"})
                if desde_hora_t is not None:
                    query = Q(ingreso_tarde__lte=desde_hora_t) & Q(salida_tarde__gte=desde_hora_t)
                    horario_valido = Horas_laborales.objects.filter(query).exists()
                    if horario_valido==False:
                        return render(request, 'register_of_assistence.html',
                                      {"form": Register_assistenceForm, "error": "Fuera del horario de la tarde"})
                if hasta_hora_t is not None:
                    query = Q(ingreso_tarde__lte=hasta_hora_t) & Q(salida_tarde__gte=hasta_hora_t)
                    horario_valido = Horas_laborales.objects.filter(query).exists()
                    if horario_valido==False:
                        return render(request, 'register_of_assistence.html',
                                      {"form": Register_assistenceForm, "error": "Fuera del horario de la tarde"})
                new_registro_de_asistencia = form.save(commit=False)
                new_registro_de_asistencia.user = request.user
                new_registro_de_asistencia.save()
                return redirect('tasks')
            else:
                return render(request, 'register_of_assistence.html',
                              {"form": Register_assistenceForm, "error": "Error"})
        except ValueError:
            return render(request, 'register_of_assistence.html', {"form": Register_assistenceForm, "error": "Error"})

@login_required
def vacation_rescheduling(request):
    if request.method == "GET":
        return render(request, 'vacation_rescheduling.html', {"form": Vacation_reschedulingForm,})
    else:
        try:
            form = Vacation_reschedulingForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'vacation_rescheduling.html', {"form": Vacation_reschedulingForm, "error": "Error creating task."+ new_task+"Hola",})

def horas_laborales_validas_mañana(desde_hora,hasta_hora):
    query = Q(ingreso_mañana__lte=desde_hora) & Q(salida_mañana__gte=desde_hora)
    query1 = Q(ingreso_tarde__lte=desde_hora) & Q(salida_tarde__gte=desde_hora)
    query2 = Q(ingreso_mañana__lte=hasta_hora) & Q(salida_mañana__gte=hasta_hora)
    query3 = Q(ingreso_tarde__lte=hasta_hora) & Q(salida_tarde__gte=hasta_hora)
    horario_valido = Horas_laborales.objects.filter(query).exists()
    horario_valido1 = Horas_laborales.objects.filter(query1).exists()
    horario_valido2 = Horas_laborales.objects.filter(query2).exists()
    horario_valido3 = Horas_laborales.objects.filter(query3).exists()
    if (horario_valido == True):
        if (horario_valido2 == True):
            mañana=True
            error_hora = False
            if hasta_hora<desde_hora:
                error_hora=True
            return mañana, error_hora
        else:
            mañana=False
            error_hora=False
    else:
        mañana = False
        error_hora=False
    return mañana, error_hora

def ingreso_de_fecha_actual(fecha):
    fecha_actual = timezone.now()
    if (fecha_actual<fecha):
        correcto=True
    else:
        if ((fecha.year==fecha_actual.year)&(fecha.month==fecha_actual.month)&(fecha.day==fecha_actual.day)):
            correcto = True
        else:
            correcto=False
    return correcto

def horas_laborales_validas_tarde(desde_hora,hasta_hora):
    query1 = Q(ingreso_tarde__lte=desde_hora) & Q(salida_tarde__gte=desde_hora)
    query3 = Q(ingreso_tarde__lte=hasta_hora) & Q(salida_tarde__gte=hasta_hora)
    horario_valido1 = Horas_laborales.objects.filter(query1).exists()
    horario_valido3 = Horas_laborales.objects.filter(query3).exists()
    if (horario_valido1 == True):
        if (horario_valido3 == True):
            tarde = True
            error_hora = False
            if hasta_hora<desde_hora:
                error_hora=True
            return tarde, error_hora
        else:
            tarde = False
            error_hora=False
    else:
        tarde = False
        error_hora=False
    return tarde, error_hora

@login_required
def official_permit_for_hours(request):
    if request.method == "GET":
        return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm})
    else:
        try:
            form = Official_permit_for_hoursForm(request.POST)
            if form.is_valid():
                diferencia_horas = 0.0
                fecha = form.cleaned_data['fecha_de_salida']
                desde_hora_m = form.cleaned_data['desde_hora_m']
                hasta_hora_m = form.cleaned_data['hasta_hora_m']
                desde_hora_t = form.cleaned_data['desde_hora_t']
                hasta_hora_t = form.cleaned_data['hasta_hora_t']
                if((desde_hora_m is not None)&(hasta_hora_m is not None)):
                    resultado_m=horas_laborales_validas_mañana(desde_hora_m,hasta_hora_m)
                    if resultado_m[1]==True:
                        return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Horas introducidas en el orden incorrecto"})
                    else:
                        if resultado_m[0]==False:
                            return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Fuera del horario de la mañana"})
                        else:
                            hasta=hasta_hora_m.hour
                            desde= desde_hora_m.hour
                            hasta_min=hasta_hora_m.minute/60
                            desde_min=desde_hora_m.minute/60
                            hasta_decimal=hasta+hasta_min
                            desde_decimal=desde+desde_min
                            diferencia_horas = hasta_decimal - desde_decimal
                            diferencia_horas= round(float(diferencia_horas), 2)
                else:
                    if ((desde_hora_t is not None) & (hasta_hora_t is not None)):
                        pass
                    else:
                        return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Rango de horas no definido"})
                if ((desde_hora_t is not None) & (hasta_hora_t is not None)):
                    resultado_t=horas_laborales_validas_tarde(desde_hora_t,hasta_hora_t)
                    if resultado_t[1]==True:
                        return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Horas introducidas en el orden incorrecto"})
                    else:
                        if resultado_t[0]==False:
                            return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Fuera del horario de la tarde"})
                        else:
                            hasta=hasta_hora_t.hour
                            desde= desde_hora_t.hour
                            hasta_min=hasta_hora_t.minute/60
                            desde_min=desde_hora_t.minute/60
                            hasta_decimal=hasta+hasta_min
                            desde_decimal=desde+desde_min
                            diferencia_horas_t = hasta_decimal - desde_decimal
                            diferencia_horas=diferencia_horas_t+diferencia_horas
                            diferencia_horas= round(float(diferencia_horas), 2)

                resultado=ingreso_de_fecha_actual(fecha)
                if resultado==False:
                    return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "No puede ingresar fechas anteriores a la actual"})

                new_official_permit_for_hours = form.save(commit=False)
                new_official_permit_for_hours.user = request.user
                new_official_permit_for_hours.horas_de_permiso = diferencia_horas
                new_official_permit_for_hours.save()
                return redirect('tasks')
            else:
                return redirect('official_permit_for_hours.html')


        except ValueError:
            return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Error"})

@login_required
def personal_leave_with_pay(request):
    if request.method == "GET":
        usuario = request.user.id
        data_usuario = Data_user.objects.get(user_id=usuario)
        id_data_user = data_usuario.id
        asignar_hora_con_goce(id_data_user)
        return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm})
    else:
        try:
            form = Personal_leave_with_payForm(request.POST)
            if form.is_valid():
                diferencia_horas = 0.0
                fecha = form.cleaned_data['fecha_de_salida']
                desde_hora_m = form.cleaned_data['salida_desde_hora_m']
                hasta_hora_m = form.cleaned_data['salida_hasta_hora_m']
                desde_hora_t = form.cleaned_data['salida_desde_hora_t']
                hasta_hora_t = form.cleaned_data['salida_hasta_hora_t']
                usuario = request.user.id
                data_usuario = Data_user.objects.get(user_id=usuario)
                horas_usadas = data_usuario.horas_con_goce_de_haberes
                horas_usadas=float(horas_usadas)
                fecha_val=ingreso_de_fecha_actual(fecha)
                resultado = ingreso_de_fecha_actual(fecha)
                if horas_usadas >= 8.0:
                    return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                            "error": "Usted ya ha ocupado 8 horas de permiso con goce de haberes"})

                if resultado == False:
                    return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                              "error": "No puede ingresar fechas anteriores a la actual"})

                if fecha_val==False:
                    return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                            "error": "La fecha debe ser posterior al día de hoy"})




                if ((desde_hora_m is not None) & (hasta_hora_m is not None)):
                    resultado_m = horas_laborales_validas_mañana(desde_hora_m, hasta_hora_m)
                    if resultado_m[1] == True:
                        return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                                  "error": "Horas introducidas en el orden incorrecto"})
                    else:
                        if resultado_m[0] == False:
                            return render(request, 'personal_leave_with_pay.html',
                                          {"form": Personal_leave_with_payForm,
                                           "error": "Fuera del horario de la mañana"})
                        else:
                            hasta = hasta_hora_m.hour
                            desde = desde_hora_m.hour
                            hasta_min = hasta_hora_m.minute / 60
                            desde_min = desde_hora_m.minute / 60
                            hasta_decimal = hasta + hasta_min
                            desde_decimal = desde + desde_min
                            diferencia_horas = hasta_decimal - desde_decimal
                            diferencia_horas = round(float(diferencia_horas), 2)
                else:
                    if ((desde_hora_t is not None) & (hasta_hora_t is not None)):
                        pass
                    else:
                        return render(request, 'personal_leave_with_pay.html',
                                      {"form": Personal_leave_with_payForm, "error": "Rango de horas no definido"})
                if ((desde_hora_t is not None) & (hasta_hora_t is not None)):
                    resultado_t = horas_laborales_validas_tarde(desde_hora_t, hasta_hora_t)
                    if resultado_t[1] == True:
                        return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                                  "error": "Horas introducidas en el orden incorrecto"})
                    else:
                        if resultado_t[0] == False:
                            return render(request, 'personal_leave_with_pay.html',
                                          {"form": Personal_leave_with_payForm,
                                           "error": "Fuera del horario de la tarde"})
                        else:
                            hasta = hasta_hora_t.hour
                            desde = desde_hora_t.hour
                            hasta_min = hasta_hora_t.minute / 60
                            desde_min = desde_hora_t.minute / 60
                            hasta_decimal = hasta + hasta_min
                            desde_decimal = desde + desde_min
                            diferencia_horas_t = hasta_decimal - desde_decimal
                            diferencia_horas=diferencia_horas_t+diferencia_horas
                            diferencia_horas= round(float(diferencia_horas), 2)

                if diferencia_horas<0.50:
                    return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm,
                                                                            "error": "No se puede solicitar un permiso menor a 30 minutos"})
                horas_solicitadas = diferencia_horas + horas_usadas
                if horas_solicitadas>2.0:
                    #Solicitamos al HTML que exija fecha y horarios de compensación
                    pass
                else:
                    new_personal_leave_with_pay=form.save(commit=False)
                    new_personal_leave_with_pay.user=request.user
                    new_personal_leave_with_pay.save()
                    data_usuario.horas_con_goce_de_haberes=horas_solicitadas
                    data_usuario.save()

                return redirect('tasks')
        except ValueError:
            return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm, "error": "Error"})

@login_required
def vacation_account_request(request):
    id_user = request.user.id
    data_vacation = Data_user.objects.get(user_id=id_user)
    dias_de_vacacion = data_vacation.dias_de_vacacion
    if request.method == "GET":
        if dias_de_vacacion<=0:
            return redirect('no_tiene_vacacion')
        else:
            return render(request, 'vacation_account_request.html', {"form": Vacation_account_requestForm,'dias_de_vacacion': dias_de_vacacion,})
    else:
        try:
            form = Vacation_account_requestForm(request.POST)
            if form.is_valid():
                fecha = form.cleaned_data['fecha_de_solicitud']
                desde_fecha_a = form.cleaned_data['fecha_solicitada1']
                hasta_fecha_a = form.cleaned_data['fecha_solicitada1_hasta']
                desde_fecha_b = form.cleaned_data['fecha_solicitada2']
                hasta_fecha_b = form.cleaned_data['fecha_solicitada2_hasta']
                desde_fecha_c = form.cleaned_data['fecha_solicitada3']
                hasta_fecha_c = form.cleaned_data['fecha_solicitada3_hasta']
                dias_solicitados = form.cleaned_data['dias_habiles_programados']
                if dias_solicitados>dias_de_vacacion:
                    return render(request, 'vacation_account_request.html',
                                  {"form": Vacation_account_requestForm, "error": "No puede solicitar mas dias de vacación de los que tiene disponibles",
                                   'dias_de_vacacion': dias_de_vacacion, })
                if((desde_fecha_c is None)&(desde_fecha_b is None)&(desde_fecha_a is None)&(hasta_fecha_c is None)&(hasta_fecha_b is None)&(hasta_fecha_a is None)):
                    return render(request, 'vacation_account_request.html',
                                  {"form": Vacation_account_requestForm, "error": "No se introdujo ninguna fecha",'dias_de_vacacion': dias_de_vacacion,})
                if(desde_fecha_a is not None):
                    if(hasta_fecha_a is None):
                        return render(request, 'vacation_account_request.html',
                                  {"form": Vacation_account_requestForm, "error": "Fecha faltante",'dias_de_vacacion': dias_de_vacacion,})
                if((desde_fecha_b is not None)):
                    if (hasta_fecha_b is None):
                        return render(request, 'vacation_account_request.html',
                                  {"form": Vacation_account_requestForm, "error": "Fecha faltante",'dias_de_vacacion': dias_de_vacacion,})
                if((desde_fecha_c is not None)):
                    if (hasta_fecha_c is None):
                        return render(request, 'vacation_account_request.html',
                                  {"form": Vacation_account_requestForm, "error": "Fecha faltante",'dias_de_vacacion': dias_de_vacacion,})
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')
        except ValueError:
            return render(request, 'vacation_account_request.html', {"form": Vacation_account_requestForm, "error": "Error",'dias_de_vacacion': dias_de_vacacion,})

# @permission_required
def no_tiene_vacacion(request):
    return render(request, 'no_tiene_vacacion.html')

def home(request):
    return render(request, 'home.html')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        if user.groups.filter(name='Funcionarios').exists():
            return redirect('tasks')
        else:
            return redirect('approve')

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task.'})

@login_required
def approve_detail_offitial_permit_for_hours(request, user_id):
    if request.method == 'GET':
        task = get_object_or_404(Official_permit_for_hours, pk=user_id)
        form = Official_permit_for_hoursForm(instance=task)
        return render(request, 'prueba_exitosa.html', {'task': task, 'form': form})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')