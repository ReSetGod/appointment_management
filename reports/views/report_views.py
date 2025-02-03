from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from core.models import Appointment, User, Doctor
from core.utils import is_allowed_to_create_reports
from reports.utils import generate_report, ReportFormat, ReportType, get_date_range
from django.utils import timezone
from django.contrib import messages


# Vista para renderizar el template de generar reporte
@user_passes_test(is_allowed_to_create_reports)
@login_required
def generate_report_form(request):
    return render(request, 'reports/generate_report.html')


# Vista para manegar la generación de reportes
@login_required
def generate_report_file(request):
    report_type = request.GET.get('report_type')
    report_format = request.GET.get('format', 'pdf')

    # Validar tipo de reporte
    if not report_type:
        messages.error(request, 'Por favor seleccione un tipo de reporte.')
        return redirect('reports:generate_report_form')

    # Continuar con la generación del reporte
    if report_type == 'appointments':
        return appointment_report(request)
    elif report_type == 'patients':
        return patients_report(request)
    elif report_type == 'doctors':
        return doctors_report(request)


@login_required
def appointment_report(request):
    report_format = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    appointments = Appointment.objects.select_related(
        'patient', 'doctor', 'speciality'
    )

    try:
        date_range = get_date_range(start_date, end_date)
        if date_range:
            appointments = appointments.filter(appointment_date__range=[
                date_range.get('gte', Appointment.objects.earliest(
                    'appointment_date').appointment_date),
                date_range.get('lte', timezone.now().date())
            ])
    except ValueError:
        messages.error(request, 'Formato de fecha inválido')
        return redirect('reports:generate_report_form')

    appointments = appointments.values(
        'id',
        'appointment_date',
        'appointment_time',
        'status',
        'patient__first_name',
        'patient__last_name',
        'doctor__first_name',
        'doctor__last_name',
        'speciality__name'
    ).order_by('appointment_date', 'appointment_time')

    data = list(appointments)

    try:
        report = generate_report(
            ReportType.APPOINTMENTS,
            ReportFormat(report_format),
            data
        )
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        return redirect('reports:generate_report_form')

    content_types = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.ms-excel',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    extensions = {
        'pdf': 'pdf',
        'excel': 'xlsx',
        'docx': 'docx'
    }

    filename = f"appointments_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{extensions[report_format]}"

    response = HttpResponse(
        report,
        content_type=content_types[report_format]
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def patients_report(request):
    report_format = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    patients = User.objects.filter(groups__name='Paciente')

    try:
        date_range = get_date_range(start_date, end_date)
        if date_range:
            patients = patients.filter(date_joined__range=[
                date_range.get('gte', User.objects.earliest(
                    'date_joined').date_joined),
                date_range.get('lte', timezone.now())
            ])
    except ValueError:
        messages.error(request, 'Formato de fecha inválido')
        return redirect('reports:generate_report_form')

    patients = patients.values(
        'id', 'first_name', 'last_name', 'email',
        'identification', 'phone_number', 'birth_date', 'genre'
    )

    data = list(patients)

    try:
        report = generate_report(
            ReportType.PATIENTS,
            ReportFormat(report_format),
            data
        )
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        return redirect('reports:generate_report_form')

    content_types = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.ms-excel',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    extensions = {
        'pdf': 'pdf',
        'excel': 'xlsx',
        'docx': 'docx'
    }

    filename = f"patients_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{extensions[report_format]}"

    response = HttpResponse(
        report,
        content_type=content_types[report_format]
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def doctors_report(request):
    report_format = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    doctors = Doctor.objects.select_related('specialities')

    try:
        date_range = get_date_range(start_date, end_date)
        if date_range:
            doctors = doctors.filter(created_at__range=[
                date_range.get('gte', Doctor.objects.earliest(
                    'created_at').created_at),
                date_range.get('lte', timezone.now())
            ])
    except ValueError:
        messages.error(request, 'Formato de fecha inválido')
        return redirect('reports:generate_report_form')

    doctors = doctors.values(
        'id', 'first_name', 'last_name', 'email',
        'identification', 'phone_number', 'specialities__name'
    )

    data = list(doctors)

    try:
        report = generate_report(
            ReportType.DOCTORS,
            ReportFormat(report_format),
            data
        )
    except Exception as e:
        messages.error(request, f'Error al generar el reporte: {str(e)}')
        return redirect('reports:generate_report_form')

    content_types = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.ms-excel',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    extensions = {
        'pdf': 'pdf',
        'excel': 'xlsx',
        'docx': 'docx'
    }

    filename = f"doctors_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{extensions[report_format]}"

    response = HttpResponse(
        report,
        content_type=content_types[report_format]
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
