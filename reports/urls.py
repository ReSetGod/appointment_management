from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.generate_report_form, name='generate_report_form'),
    path('generate/', views.generate_report_file, name='generate_report'),
    path('appointments/', views.appointment_report, name='appointment_report'),
    path('patients/', views.patients_report, name='patients_report'),
    path('doctors/', views.doctors_report, name='doctors_report'),

    # Vista principal del dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Vistas para cargar los datos de las gráficas
    path('patient-concurrence/', views.patient_concurrence,
         name='patient_concurrence'),
    path('most-requested-specialities/',
         views.most_requested_specialities, name='most_requested_specialities'),
    path('most-recurrent-diseases/', views.most_recurrent_diseases,
         name='most_recurrent_diseases'),
    path('doctor-ratings/', views.doctor_ratings, name='doctor_ratings'),
]
