from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.generate_report_form, name='generate_report_form'),
    path('generate/', views.generate_report_file, name='generate_report'),
    path('appointments/', views.appointment_report, name='appointment_report'),
    path('patients/', views.patients_report, name='patients_report'),
    path('doctors/', views.doctors_report, name='doctors_report'),
]
