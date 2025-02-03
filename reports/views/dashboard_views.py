from django.http import JsonResponse
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from core.models import Appointment, MedicalHistory, Rating
from core.utils import is_manager


@user_passes_test(is_manager)
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


@login_required
def patient_concurrence(request):
    try:
        time_frame = int(request.GET.get('time_frame', 30))
        end_date = timezone.localtime().date()
        # Sustraer días para obtener la fecha de inicio
        start_date = end_date - timedelta(days=time_frame - 1)

        data = (
            Appointment.objects.filter(
                appointment_date__range=[start_date,
                                         end_date]  # rango incluyente
            ).values('appointment_date')
            .annotate(total=Count('id'))
            .order_by('appointment_date')
        )

        # Asegurar que se incluyan todos los días en el rango
        date_range = {(start_date + timedelta(days=x)).strftime('%d/%m/%Y'): 0
                      for x in range((end_date - start_date).days + 1)}

        # Actualizar los valores de los días con citas
        for entry in data:
            date_str = timezone.localtime(
                timezone.make_aware(datetime.combine(
                    entry['appointment_date'], datetime.min.time()))
            ).strftime('%d/%m/%Y')
            date_range[date_str] = entry['total']

        response_data = {
            'labels': list(date_range.keys()),
            'data': list(date_range.values()),
        }
        return JsonResponse({'success': True, 'data': response_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def most_requested_specialities(request):
    try:
        time_frame = int(request.GET.get('time_frame', 30))
        end_date = timezone.localtime().date()
        start_date = end_date - timedelta(days=time_frame)

        data = (
            Appointment.objects.filter(
                appointment_date__range=[start_date, end_date]
            ).values('speciality__name')
            .exclude(speciality__name__isnull=True)
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

        response_data = {
            'labels': [entry['speciality__name'] for entry in data],
            'data': [entry['total'] for entry in data],
        }
        return JsonResponse({'success': True, 'data': response_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def most_recurrent_diseases(request):
    try:
        time_frame = int(request.GET.get('time_frame', 30))
        end_date = timezone.localtime().date()
        start_date = end_date - timedelta(days=time_frame)

        data = (
            MedicalHistory.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).values('diagnosis')
            .exclude(diagnosis='')
            .exclude(diagnosis__isnull=True)
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

        response_data = {
            'labels': [entry['diagnosis'] for entry in data],
            'data': [entry['total'] for entry in data],
        }
        return JsonResponse({'success': True, 'data': response_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def doctor_ratings(request):
    try:
        time_frame = int(request.GET.get('time_frame', 30))
        end_date = timezone.localtime().date()
        start_date = end_date - timedelta(days=time_frame)

        data = (
            Rating.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).values('doctor__first_name', 'doctor__last_name')
            .annotate(average_score=Avg('score'))
            .order_by('-average_score')
        )

        response_data = {
            'labels': [f"Dr. {entry['doctor__first_name']} {entry['doctor__last_name']}" for entry in data],
            'data': [float(entry['average_score']) for entry in data],
        }
        return JsonResponse({'success': True, 'data': response_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
