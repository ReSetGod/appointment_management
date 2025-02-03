from core.models import Notification


def group_context(request):
    if request.user.is_authenticated:
        return {
            'is_paciente': request.user.groups.filter(name='Paciente').exists(),
            'is_administrador': request.user.groups.filter(name='Administrador').exists(),
            'is_secretaria': request.user.groups.filter(name='Secretaria').exists(),
            'is_doctor': request.user.groups.filter(name='Doctor').exists(),
            'is_manager': request.user.groups.filter(name='Gerencia').exists(),
        }
    return {}


def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            patient=request.user,
            is_read=False
        ).order_by('-created_at')
        return {
            'notifications': notifications,
            'unread_notifications': notifications,
        }
    return {'notifications': None, 'unread_notifications': None}
