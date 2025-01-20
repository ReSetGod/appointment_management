import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse

from core.forms import DoctorForm
from core.models import Doctor
from core.utils import generate_password, get_doctor_name, is_admin, is_doctor, is_patient, is_receptionist
from django.contrib.auth.models import Group


@login_required
@user_passes_test(is_admin)
def manage_doctors(request):
    return render(request, 'administrator/manage_doctors.html')


@login_required
def create_or_edit_doctor(request, doctor_id=None):
    is_editing = doctor_id is not None
    doctor = None

    # Si se está editando, obtenemos el doctor, o lanzamos 404 si no existe.
    if is_editing:
        doctor = get_object_or_404(Doctor, pk=doctor_id)

    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            try:
                doctor = form.save(commit=False)
                # Solo generamos la contraseña si es una creación.
                if not is_editing:
                    password = generate_password()
                    doctor.set_password(password)

                doctor.modified_by = request.user
                doctor.save()
                form.save_m2m()

                # Asignación de grupo para nuevos doctores.
                if not is_editing:
                    doctor_group, created = Group.objects.get_or_create(
                        name='Doctor')
                    doctor.groups.add(doctor_group)
                    messages.success(
                        request, f'Doctor creado con éxito. La contraseña generada es: {password}'
                    )
                else:
                    messages.success(request, 'Doctor actualizado con éxito.')

                return redirect('manage_doctors')

            except Exception as e:
                messages.error(
                    request, f'Error al guardar el doctor: {str(e)}')
        else:
            # Manejo detallado de errores.
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label}: {error}")

    else:
        if doctor and doctor.birth_date:
            doctor.birth_date = doctor.birth_date.strftime('%Y-%m-%d')
        form = DoctorForm(instance=doctor)

    return render(request, 'administrator/create_or_edit_doctor.html', {
        'form': form,
        'is_editing': is_editing
    })


@login_required
def delete_doctor(request):
    if request.method == 'POST':
        try:
            # Obtenemos el JSON del cuerpo de la solicitud
            body = json.loads(request.body)
            doctor_id = body.get('doctor_id')

            if not doctor_id:
                return JsonResponse({'message': 'ID de doctor no proporcionado.'}, status=400)

            # Verificamos que el doctor existe
            doctor = get_object_or_404(Doctor, id=doctor_id)

            # Eliminamos el doctor
            doctor.delete()

            return JsonResponse({'message': 'Doctor eliminado exitosamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error al eliminar el doctor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido.'}, status=405)


# Vista para cargar los doctores
@login_required
def load_doctors(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Validar acceso según el tipo de usuario
            if not (is_admin(user) or is_receptionist(user)):
                return JsonResponse({"message": "No autorizado"}, status=403)

            # Obtener los doctores desde la base de datos
            doctors = Doctor.objects.prefetch_related('specialities').all()

            # Formatear los datos en JSON
            doctors_data = []
            for doctor in doctors:
                doctors_data.append({
                    "id": doctor.id,
                    "name": get_doctor_name(doctor),
                    "identification": doctor.identification,
                    "phone_number": doctor.phone_number,
                    "address": doctor.address,
                    "city": doctor.city,
                    "birth_date": doctor.birth_date.strftime('%Y-%m-%d') if doctor.birth_date else "",
                    "genre": doctor.get_genre_display(),
                    "specialities": ", ".join([speciality.name for speciality in doctor.specialities.all()]),
                })

            return JsonResponse({"message": "Success", "doctors": doctors_data})

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


# Vista para obtener los doctores filtrados por especialidad
@login_required
def get_doctors_by_specialty(request, specialty_id):
    doctors = list(Doctor.objects.filter(
        specialities__id=specialty_id).values('id', 'first_name', 'last_name'))

    if (len(doctors) > 0):
        data = {'message': "Success", 'doctors': doctors}
    else:
        data = {'message': "Not Found"}

    return JsonResponse(data)


# Vista para renderizar la página de búsqueda de doctores
@login_required
@user_passes_test(is_patient)
def search_doctors(request):
    return render(request, 'patient/search_doctors.html')


# Vista para renderizar la página de calendario de doctores
@login_required
@user_passes_test(is_doctor)
def doctor_calendar(request):
    return render(request, 'doctor/doctor_calendar.html')
