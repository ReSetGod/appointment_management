import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from core.forms import SpecialityForm
from core.models import Speciality
from core.utils import is_admin, is_receptionist


@login_required
@user_passes_test(is_admin)
def manage_specialities(request):
    return render(request, 'administrator/manage_specialities.html')


@login_required
def create_or_edit_speciality(request, speciality_id=None):
    is_editing = speciality_id is not None
    speciality = None

    if is_editing:
        speciality = get_object_or_404(Speciality, pk=speciality_id)

    if request.method == 'POST':
        form = SpecialityForm(request.POST, instance=speciality)
        if form.is_valid():
            try:
                speciality = form.save(commit=False)
                speciality.modified_by = request.user
                speciality.save()
                messages.success(
                    request, 'Especialidad guardada con éxito.')
                return redirect('manage_specialities')
            except Exception as e:
                messages.error(
                    request, f'Error al guardar la especialidad: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{form.fields[field].label}: {error}")
    else:
        form = SpecialityForm(instance=speciality)

    return render(request, 'administrator/create_or_edit_speciality.html', {
        'form': form,
        'is_editing': is_editing
    })


@login_required
def delete_speciality(request):
    if request.method == 'POST':
        try:
            # Obtenemos el JSON del cuerpo de la solicitud
            body = json.loads(request.body)
            speciality_id = body.get('speciality_id')

            if not speciality_id:
                return JsonResponse({'message': 'ID de especialidad no proporcionado.'}, status=400)

            # Verificamos que la especialidad existe
            speciality = get_object_or_404(Speciality, id=speciality_id)

            # Eliminamos la especialidad
            speciality.delete()

            return JsonResponse({'message': 'Especialidad eliminada exitosamente.'}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Error al eliminar la especialidad: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido.'}, status=405)


@login_required
def load_specialities(request):
    if request.method == 'GET':
        try:
            user = request.user

            # Validar acceso según el tipo de usuario
            if not (is_admin(user) or is_receptionist(user)):
                return JsonResponse({"message": "No autorizado"}, status=403)

            # Obtener las especialidades desde la base de datos
            specialities = Speciality.objects.all()

            # Formatear los datos en JSON
            specialities_data = []
            for speciality in specialities:
                specialities_data.append({
                    "id": speciality.id,
                    "name": speciality.name,
                    "description": speciality.description,
                    'created_at': speciality.created_at.strftime('%Y-%m-%d  %H:%M'),
                    "status": "Activo" if speciality.status else "Inactivo",
                })

            return JsonResponse({"message": "Success", "specialities": specialities_data})

        except Exception as e:
            return JsonResponse({"message": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


# Vista para obtenet las especialidades
@login_required
def get_specialities(request):
    # Obtener el parámetro de búsqueda, si existe
    search_query = request.GET.get('search', '').lower()

    # Filtrar las especialidades por nombre y estado activo
    if search_query:
        specialities = list(Speciality.objects.filter(
            name__icontains=search_query, status=True).values('id', 'name', 'description'))
    else:
        # Si no hay búsqueda, devolver solo las especialidades activas
        specialities = list(Speciality.objects.filter(
            status=True).values('id', 'name', 'description'))

    if len(specialities) > 0:
        data = {'message': "Success", 'specialities': specialities}
    else:
        data = {'message': "Not Found"}

    return JsonResponse(data)
