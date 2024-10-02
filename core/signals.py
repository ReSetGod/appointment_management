from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_currentuser.middleware import get_current_authenticated_user
from .models import Speciality, Doctor, MedicalHistory
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
import logging

# Configurar el logger
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Speciality)
@receiver(pre_save, sender=Doctor)
@receiver(pre_save, sender=MedicalHistory)
def set_modified_by(sender, instance, **kwargs):
    try:
        user = get_current_authenticated_user()
        if user and user.is_authenticated:
            instance.modified_by = user
        else:
            logger.warning(
                "El usuario no está autenticado o no se pudo obtener el usuario actual.")
    except Exception as e:
        logger.error(
            f"Error al establecer modified_by en {sender.__name__}: {e}")


@receiver(user_logged_in)
def clear_login_message(sender, request, user, **kwargs):
    try:
        # Obtiene el almacenamiento de mensajes
        storage = messages.get_messages(request)
        # Marca los mensajes como usados, lo que los elimina
        storage.used = True
    except Exception as e:
        logger.error(f"Error al limpiar los mensajes de inicio de sesión: {e}")
