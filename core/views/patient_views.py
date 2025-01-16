import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from core.forms import UserForm
from core.models import User
from django.contrib.auth.models import Group
from core.utils import generate_password, get_patient_name, is_admin, is_patient, is_receptionist


# Vista para renderizar la página para gestionar los pacientes
@login_required
@user_passes_test(is_receptionist)
def manage_patients(request):
    return render(request, 'receptionist/manage_patients.html')


# Crear o editar un paciente
@login_required
def create_or_edit_patient(request, patient_id=None):
    is_editing = patient_id is not None
    patient = None

    # Si se está editando, obtenemos el usuario, o lanzamos 404 si no existe.
    if is_editing:
        patient = get_object_or_404(User, pk=patient_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=patient)
        if form.is_valid():
            try:
                patient = form.save(commit=False)

                # Solo generamos la contraseña si es una creación.
                if not is_editing:
                    password = generate_password()
                    patient.set_password(password)

                patient.modified_by = request.user
                patient.save()

                # Asignación de grupo para nuevos pacientes.
                if not is_editing:
                    patient_group, created = Group.objects.get_or_create(
                        name='Paciente')
                    patient.groups.add(patient_group)
                    messages.success(
                        request, f'Paciente creado con éxito. La contraseña generada es: {password}'
                    )
                else:
                    messages.success(
                        request, 'Paciente actualizado con éxito.')

                return redirect('manage_patients')

            except Exception as e:
                messages.error(
                    request, f'Error al guardar el paciente: {str(e)}')
        else:
            # Manejo detallado de errores.
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label}: {error}")

    else:
        if patient and patient.birth_date:
            patient.birth_date = patient.birth_date.strftime('%Y-%m-%d')
        form = UserForm(instance=patient)

    return render(request, 'receptionist/create_or_edit_patient.html', {
        'form': form,
        'is_editing': is_editing
    })


# Eliminar un paciente
@login_required
def delete_patient(request):
    if request.method == 'POST':
        try:
            # Obtenemos el JSON del cuerpo de la solicitud
            body = json.loads(request.body)
            patient_id = body.get('patient_id')

            if not patient_id:
                return JsonResponse({'message': 'ID de paciente no proporcionado.'}, status=400)

            # Verificamos que el usuario existe
            patient = get_object_or_404(User, id=patient_id)

            # Eliminamos el usuario
            patient.delete()

            return JsonResponse({'message': 'Paciente eliminado exitosamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error al eliminar el paciente: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido.'}, status=405)


# Cargar pacientes
def load_patients(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Validar acceso según el tipo de usuario
            if not (is_admin(user) or is_receptionist(user)):
                return JsonResponse({"message": "No autorizado"}, status=403)

            # Obtener los usuarios del grupo Paciente desde la base de datos
            patients = User.objects.filter(groups__name='Paciente')

            # Formatear los datos en JSON
            patients_data = []
            for patient in patients:
                patients_data.append({
                    "id": patient.id,
                    "name": get_patient_name(patient),
                    "identification": patient.identification,
                    "phone_number": patient.phone_number,
                    "address": patient.address,
                    "city": patient.city,
                    "birth_date": patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else "",
                    "genre": patient.get_genre_display(),
                })

            return JsonResponse({"message": "Success", "patients": patients_data})

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)
