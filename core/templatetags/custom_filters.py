from django import template
from datetime import date

register = template.Library()


@register.filter
def age(birth_date):
    if birth_date:
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return ''


@register.filter
def genre_display(value):
    genre_map = {
        'M': 'Masculino',
        'F': 'Femenino'
    }
    return genre_map.get(value, value)


@register.filter
def doctor_title(doctor):
    return 'Dra.' if doctor.genre == 'F' else 'Dr.'


@register.filter
def status_display(value):
    status_map = {
        'PENDING': 'Pendiente',
        'CONFIRMED': 'Confirmada',
        'CANCELLED': 'Cancelada',
        'ATTENDED': 'Atendida',
        'NO_SHOW': 'No asistió'
    }
    return status_map.get(value, value)
