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
import re
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
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'register_of_assistence.html', {"form": Register_assistenceForm, "error": "Error creating task."+ new_task+"Hola"})

@login_required
def vacation_rescheduling(request):
    id_user = request.user.id
    data_vacation = Data_user.objects.get(user_id=id_user)
    dias_de_vacacion = data_vacation.dias_de_vacacion
    if request.method == "GET":
        return render(request, 'vacation_rescheduling.html', {"form": Vacation_reschedulingForm,'dias_de_vacacion': dias_de_vacacion,})
    else:
        try:
            form = Vacation_reschedulingForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'vacation_rescheduling.html', {"form": Vacation_reschedulingForm, "error": "Error creating task."+ new_task+"Hola",'dias_de_vacacion': dias_de_vacacion,})

@login_required
def official_permit_for_hours(request):
    if request.method == "GET":
        return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm})
    else:
        try:
            form = Official_permit_for_hoursForm(request.POST)
            if form.is_valid():
                desde_hora = form.cleaned_data['desde_hora']
                query = Q(ingreso_mañana__lte=desde_hora) & Q(salida_mañana__gte=desde_hora)
                query1 = Q(ingreso_tarde__lte=desde_hora) & Q(salida_tarde__gte=desde_hora)
                horario_valido = Horas_laborales.objects.filter(query).exists()
                horario_valido1 = Horas_laborales.objects.filter(query1).exists()
                if ((horario_valido==True)|(horario_valido1==True)):
                    new_task = form.save(commit=False)
                    new_task.user = request.user
                    new_task.save()
                    return redirect('tasks')
                else:
                    return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm,
                                                                              "error": "Fuera del horario laboral"})

        except ValueError:
            return render(request, 'official_permit_for_hours.html', {"form": Official_permit_for_hoursForm, "error": "Error creating task."+ new_task+"Hola"})

@login_required
def personal_leave_with_pay(request):
    if request.method == "GET":
        return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm})
    else:
        try:
            form = Personal_leave_with_payForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'personal_leave_with_pay.html', {"form": Personal_leave_with_payForm, "error": "Error creating task."+ new_task+"Hola"})

@login_required
def vacation_account_request(request):
    if request.method == "GET":
        return render(request, 'vacation_account_request.html', {"form": Vacation_account_requestForm})
    else:
        try:
            form = Vacation_account_requestForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'vacation_account_request.html', {"form": Vacation_account_requestForm, "error": "Error creating task."+ new_task+"Hola"})

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