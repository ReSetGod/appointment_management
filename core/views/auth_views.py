from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from core.forms import CustomEmailForm
from allauth.account.models import EmailAddress


# Vista para renderizar la página para cambiar el correo
@login_required
def render_email_page(request):
    # Obtén el correo directamente del usuario autenticado
    current_email = request.user.email

    # Prepara el formulario sin datos enviados
    form = CustomEmailForm(user=request.user)

    # Renderiza el template con el correo actual
    return render(request, 'account/email.html', {
        'form': form,
        'current_email': current_email,
    })


# Vista para cambiar email
@login_required
def update_email_view(request):
    if request.method == 'POST':

        form = CustomEmailForm(request.POST, user=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['email']

            # Obtén el correo actual para eliminarlo
            current_email_obj = EmailAddress.objects.filter(
                user=request.user, primary=True).first()

            if current_email_obj:
                current_email_obj.delete()

            # Crea el nuevo correo
            EmailAddress.objects.create(
                user=request.user, email=new_email, primary=True, verified=False
            )

            # Actualiza el modelo User
            request.user.email = new_email
            request.user.save()

            messages.success(
                request, "Correo electrónico actualizado correctamente."
            )
            return redirect('configuration')
        else:
            messages.error(request, "Hubo un error al actualizar el correo.")

    # Redirige a la página de configuración si no es POST
    return redirect('configuration')


# Vista para eliminar usuarios
@login_required
def delete_user(request):
    try:
        if request.method == 'POST':
            user = request.user
            user.delete()
            messages.success(
                request, "Tu cuenta ha sido eliminada exitosamente.")
            return redirect('account_login')
    except Exception as e:
        messages.error(request, "Hubo un error al eliminar tu cuenta.")
        return redirect('configuration')
