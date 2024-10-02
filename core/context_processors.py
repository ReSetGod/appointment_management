def group_context(request):
    if request.user.is_authenticated:
        return {
            'is_paciente': request.user.groups.filter(name='Paciente').exists(),
            'is_administrador': request.user.groups.filter(name='Administrador').exists(),
            'is_secretaria': request.user.groups.filter(name='Secretaria').exists(),
            'is_doctor': request.user.groups.filter(name='Doctor').exists(),
        }
    return {}
