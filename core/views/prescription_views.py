from django.http import FileResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction

from core.forms import PrescriptionForm
from django.core.files.base import ContentFile
from core.models import MedicalHistory, Prescription
from core.utils import generate_pdf


@login_required
def create_prescription(request, medical_history_id):
    try:
        medical_history = get_object_or_404(
            MedicalHistory, id=medical_history_id)

        if not hasattr(request.user, 'doctor'):
            raise PermissionDenied(
                "No tienes permiso para crear recetas en esta historia médica.")

        if request.method == 'POST':
            form = PrescriptionForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Borrar receta existente si existe una
                        existing_prescription = medical_history.prescriptions.first()
                        if existing_prescription:
                            try:
                                # Elegir el archivo de receta si esta abierto
                                if hasattr(existing_prescription.pdf_file, 'file'):
                                    existing_prescription.pdf_file.file.close()

                                # Borrar archivo PDF de la receta
                                if existing_prescription.pdf_file:
                                    storage = existing_prescription.pdf_file.storage
                                    if storage.exists(existing_prescription.pdf_file.name):
                                        storage.delete(
                                            existing_prescription.pdf_file.name)

                                # Limpiar campo de archivo PDF
                                existing_prescription.pdf_file = None
                                existing_prescription.save()

                                # Borrar receta
                                existing_prescription.delete()

                            except Exception as e:
                                messages.error(
                                    request, f'Error al eliminar receta existente: {str(e)}')
                                raise

                        # Generar nueva receta
                        prescription = form.save(commit=False)
                        prescription.medical_history = medical_history
                        prescription.doctor = request.user.doctor
                        prescription.save()

                        # Generar archivo PDF
                        context = {
                            'prescription': prescription,
                            'doctor_name': request.user.get_full_name(),
                            'patient_name': medical_history.patient.get_full_name(),
                            'issued_at': prescription.issued_at.strftime('%d/%m/%Y'),
                        }

                        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"prescription_{prescription.id}_{timestamp}.pdf"

                        try:
                            pdf = generate_pdf(
                                'doctor/prescription_template.html', context)
                            prescription.pdf_file.save(
                                filename, ContentFile(pdf), save=True)
                            messages.success(
                                request, 'Receta creada exitosamente.')
                            return redirect('manage_diagnosis')
                        except Exception as e:
                            if prescription.pdf_file:
                                prescription.pdf_file.delete(save=False)
                            prescription.delete()
                            messages.error(
                                request, f'Error al generar el PDF: {str(e)}')
                            raise

                except Exception as e:
                    messages.error(
                        request, f'Error al procesar la receta: {str(e)}')

        else:
            form = PrescriptionForm()

        return render(request, 'doctor/create_prescription.html',
                      {'form': form, 'history': medical_history})

    except Exception as e:
        messages.error(request, 'Error inesperado al procesar la solicitud.')
        return redirect('home')


# Vista para descargar recetas
@login_required
def download_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)

    if prescription.pdf_file:
        response = FileResponse(
            prescription.pdf_file.open(),
            content_type='application/pdf',
            as_attachment=True,
            filename=f"Receta_{prescription.id}.pdf"
        )
        return response
    return HttpResponse("La receta no está disponible.", status=404)
