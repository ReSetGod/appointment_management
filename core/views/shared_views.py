from datetime import datetime, time
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from core.forms import UserUpdateForm
from core.models import Appointment, User


@login_required
def home(request):
    return render(request, 'shared/home.html')


# Configuración
@login_required
def configuration(request):
    try:
        if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Tu información ha sido actualizada exitosamente."
                )
                return JsonResponse({"success": True, "message": "Información actualizada exitosamente."})
            else:
                messages.error(
                    request, "Hubo un error al actualizar tu información. Por favor, revisa los campos."
                )
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
        else:
            form = UserUpdateForm(instance=request.user)
    except Exception as e:
        messages.error(
            request, "Ocurrió un error inesperado. Por favor, intenta de nuevo."
        )
        return JsonResponse({"success": False, "error": "Ocurrió un error inesperado."}, status=500)

    return render(request, "shared/configuration.html", {"form": form})


# Vista para obtener los horarios disponibles
@login_required
def get_available_times(request, doctor_id, date):
    try:
        # Recuperar el horario seleccionado si se envió como parámetro
        selected_time = request.GET.get("selected_time")

        # Convertir la fecha de string a objeto date
        appointment_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Definir los turnos de la mañana y la tarde con intervalos de 30 minutos
        morning_shift = [time(9, 0), time(9, 30), time(10, 0), time(
            10, 30), time(11, 0), time(11, 30), time(12, 0)]
        afternoon_shift = [time(16, 0), time(16, 30), time(
            17, 0), time(17, 30), time(18, 0)]

        # Combinar ambos turnos
        all_shifts = morning_shift + afternoon_shift

        # Obtener la hora actual en la zona horaria local
        current_datetime = timezone.localtime()

        # Validar si la fecha seleccionada es hoy
        if appointment_date == current_datetime.date():
            # Si la fecha es hoy, eliminar horarios que ya han pasado
            current_time = current_datetime.time()

            # Filtrar los turnos que son pasados
            all_shifts = [
                shift for shift in all_shifts if shift > current_time]

        # Obtener las citas del doctor en la fecha seleccionada
        appointments = Appointment.objects.filter(
            doctor_id=doctor_id, appointment_date=appointment_date, status='CONFIRMED')

        # Obtener los horarios ocupados
        occupied_times = [
            appointment.appointment_time for appointment in appointments]

        # Filtrar los horarios disponibles
        available_times = [
            shift.strftime("%H:%M") for shift in all_shifts
            if shift.strftime("%H:%M") not in [t.strftime("%H:%M") for t in occupied_times]
        ]

        # Verificar si existe un horario seleccionado y agregarlo a los horarios disponibles
        if selected_time and selected_time not in available_times:
            # Agregar el horario seleccionado
            available_times.append(selected_time)
            available_times.sort()  # Ordenar los horarios nuevamente

        # Retornar los horarios disponibles
        if available_times:
            data = {'message': 'Success', 'available_times': available_times}
        else:
            data = {'message': 'No Available Times'}
    except Exception as e:
        data = {'message': f'Error: {str(e)}'}

    return JsonResponse(data)


# Vista para buscar pacientes
@login_required
def search_patients(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        if query:
            patients = User.objects.filter(
                groups__name='Paciente'
            ).filter(
                Q(identification__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).values('id', 'first_name', 'last_name', 'identification')

            return JsonResponse({'patients': list(patients)}, safe=False)
        else:
            return JsonResponse({'patients': []}, safe=False)
