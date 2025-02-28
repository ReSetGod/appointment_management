from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    maternal_surname = models.CharField(max_length=30, blank=True, null=True)
    identification = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    GENRE_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    genre = models.CharField(
        max_length=1, choices=GENRE_CHOICES, blank=False, null=False)

    def __str__(self):
        return self.username


class Speciality(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()
    detailed_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return self.name


class Doctor(User):
    specialities = models.ManyToManyField(Speciality)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_doctors')

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'

    def __str__(self):
        return f'{self.username} - {", ".join([speciality.name for speciality in self.specialities.all()])}'


class Appointment(models.Model):
    patient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(
        'Doctor', on_delete=models.CASCADE, related_name='doctor_appointments')
    speciality = models.ForeignKey(
        'Speciality', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()

    # Campos adicionales
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendiente'),
            ('CONFIRMED', 'Confirmada'),
            ('CANCELLED', 'Cancelada'),
            ('ATTENDED', 'Atendida'),
            ('NO_SHOW', 'No asistió'),
        ],
        default='CONFIRMED'
    )

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f'{self.patient.first_name} {self.patient.last_name} - {self.appointment_date} - {self.appointment_time}'

    def clean(self):
        # Obtener la fecha y hora actuales en la zona horaria local
        current_datetime = timezone.localtime()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        # Validación para evitar duplicados a nivel de modelo, considerando solo citas confirmadas
        if self.status == 'CONFIRMED' and Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status='CONFIRMED'  # Solo se consideran las citas confirmadas
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f'Este doctor ya tiene una cita confirmada en esta hora y fecha'
            )

        # Validación para que la fecha de la cita no sea en el pasado
        if self.appointment_date < current_date:
            raise ValidationError(
                'La fecha de la cita no puede ser en el pasado.')

        # Validación para que la hora de la cita para el mismo día no sea anterior a la hora actual.
        if self.appointment_date == current_date and self.appointment_time < current_time:
            raise ValidationError(
                'La hora de la cita no puede ser en el pasado.')

        # Validación para máximo dos citas con diferentes médicos en el mismo día
        if self.status == 'CONFIRMED':
            same_day_appointments = Appointment.objects.filter(
                patient=self.patient,
                appointment_date=self.appointment_date,
                status='CONFIRMED'
            ).exclude(pk=self.pk).values('doctor').distinct()
            if len(same_day_appointments) >= 2:
                raise ValidationError(
                    'No puedes reservar más de dos citas con diferentes médicos en el mismo día.'
                )

        # Validación para evitar citas duplicadas en la misma fecha y hora para el mismo paciente
        if self.status == 'CONFIRMED' and Appointment.objects.filter(
            patient=self.patient,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
            status='CONFIRMED'
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                'Ya tienes una cita en este horario y fecha. Por favor, elige otro horario.'
            )

    def save(self, *args, **kwargs):
        # Llamada a full_clean para realizar todas las validaciones (incluyendo clean)
        self.full_clean()
        super().save(*args, **kwargs)


class MedicalHistory(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='medical_histories')
    doctor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnosed_histories'
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='medical_histories', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_histories')
    diagnosis = models.TextField()
    treatment = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Activo'),
            ('ARCHIVED', 'Archivado'),
            ('PENDING', 'Pendiente'),
        ],
        default='ACTIVE'
    )

    def __str__(self):
        return f'Historial Médico de {self.patient.username} - {self.created_at.strftime("%Y-%m-%d")}'


class Prescription(models.Model):
    medical_history = models.ForeignKey(
        MedicalHistory, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='issued_prescriptions')
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    medication_details = models.TextField(
        help_text="Detalles del medicamento: nombre, gramos, tabletas, etc.")
    instructions = models.TextField(
        help_text="Indicaciones: cómo y cuándo tomar el medicamento.")
    pdf_file = models.FileField(
        upload_to='prescriptions/', blank=True, null=True)

    class Meta:
        verbose_name = 'Receta Médica'
        verbose_name_plural = 'Recetas Médicas'

    def __str__(self):
        return f'Receta de {self.doctor.username} para {self.patient.username} - {self.issued_at.strftime("%Y-%m-%d")}'


class Rating(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='rating')
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ratings_given')
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='ratings_received')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating for appointment {self.appointment.id} - {self.score}/5'


class Notification(models.Model):
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.patient.username} - {self.created_at}'


class Triage(models.Model):
    CONSCIOUSNESS_CHOICES = [
        ('ALERT', 'Alerta'),
        ('VERBAL', 'Responde a estímulo verbal'),
        ('PAIN', 'Responde a estímulo doloroso'),
        ('UNRESPONSIVE', 'No responde')
    ]

    CATEGORY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('MODERATE', 'Alerta Moderada'),
        ('SEVERE', 'Alerta Severa'),
        ('CRITICAL', 'Crítico')
    ]

    patient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='triages')
    created_at = models.DateTimeField(auto_now_add=True)
    heart_rate = models.IntegerField('Frecuencia Cardíaca')
    respiratory_rate = models.IntegerField('Frecuencia Respiratoria')
    systolic_blood_pressure = models.IntegerField('Presión Arterial Sistólica')
    oxygen_saturation = models.IntegerField('SpO2')
    consciousness_level = models.CharField(
        'Nivel de Conciencia', max_length=20, choices=CONSCIOUSNESS_CHOICES)

    # Puntajes
    heart_rate_score = models.IntegerField(default=0)
    respiratory_rate_score = models.IntegerField(default=0)
    blood_pressure_score = models.IntegerField(default=0)
    oxygen_saturation_score = models.IntegerField(default=0)
    consciousness_score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def calculate_scores(self):
        # Frecuencia Cardíaca (FC)
        if self.heart_rate >= 140 or self.heart_rate < 40:
            self.heart_rate_score = 5  # Crítico
        elif (121 <= self.heart_rate < 140) or (40 <= self.heart_rate <= 49):
            self.heart_rate_score = 3  # Alerta Severa
        elif (100 <= self.heart_rate <= 120) or (50 <= self.heart_rate <= 59):
            self.heart_rate_score = 1  # Alerta Moderada
        elif 60 <= self.heart_rate <= 100:
            self.heart_rate_score = 0  # Normal

    # Rango de respiración (FR)
        if self.respiratory_rate > 30 or self.respiratory_rate <= 6:
            self.respiratory_rate_score = 5  # Crítico
        elif (25 <= self.respiratory_rate <= 30) or (6 < self.respiratory_rate <= 8):
            self.respiratory_rate_score = 3  # Alerta Severa
        elif (21 <= self.respiratory_rate <= 24) or (9 <= self.respiratory_rate <= 11):
            self.respiratory_rate_score = 1  # Alerta Moderada
        elif 12 <= self.respiratory_rate <= 20:
            self.respiratory_rate_score = 0  # Normal

    # Presión arterial (PA)
        if self.systolic_blood_pressure > 180 or self.systolic_blood_pressure < 70:
            self.blood_pressure_score = 5  # Crítico
        elif (161 <= self.systolic_blood_pressure <= 180) or (70 <= self.systolic_blood_pressure <= 79):
            self.blood_pressure_score = 3  # Alerta Severa
        elif (140 < self.systolic_blood_pressure <= 160) or (80 <= self.systolic_blood_pressure <= 89):
            self.blood_pressure_score = 1  # Alerta Moderada
        elif 90 <= self.systolic_blood_pressure <= 140:
            self.blood_pressure_score = 0  # Normal

    # Saturación de oxígeno (SpO2)
        if self.oxygen_saturation < 85:
            self.oxygen_saturation_score = 5  # Crítico
        elif 85 <= self.oxygen_saturation <= 89:
            self.oxygen_saturation_score = 3  # Alerta Severa
        elif 90 <= self.oxygen_saturation <= 94:
            self.oxygen_saturation_score = 1  # Alerta Moderada
        elif self.oxygen_saturation >= 95:
            self.oxygen_saturation_score = 0  # Normal

        # Conciencia score
        consciousness_scores = {
            'ALERT': 0,        # Normal
            'VERBAL': 1,       # Alerta Moderada
            'PAIN': 3,         # Alerta Severa
            'UNRESPONSIVE': 5  # Crítico
        }
        self.consciousness_score = consciousness_scores.get(
            self.consciousness_level, 0)

        # Calcular el total score
        self.total_score = (
            self.heart_rate_score +
            self.respiratory_rate_score +
            self.blood_pressure_score +
            self.oxygen_saturation_score +
            self.consciousness_score
        )

        # Clasificación basada en total_score
        if self.total_score >= 15:
            self.category = 'CRITICAL'
        elif self.total_score >= 10:
            self.category = 'SEVERE'
        elif self.total_score >= 5:
            self.category = 'MODERATE'
        else:
            self.category = 'NORMAL'

    def save(self, *args, **kwargs):
        self.calculate_scores()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
