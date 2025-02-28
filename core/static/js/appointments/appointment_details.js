// Añadir token CSRF a todas las peticiones HTMX
document.addEventListener('htmx:configRequest', (event) => {
    const csrfToken = "{{ csrf_token }}";
    event.detail.headers['X-CSRFToken'] = csrfToken;
});

// Función para manejar la respuesta después de la cancelación con SweetAlert
function handleCancellationResponse(event) {
    const response = event.detail.xhr.responseText;
    const data = JSON.parse(response);

    if (data.message) {
        // Mostrar el mensaje de confirmación con SweetAlert
        Swal.fire({
            title: '¡Éxito!',
            text: data.message,
            icon: 'success',
            confirmButtonText: 'OK',
            confirmButtonColor: '#0077B6'
        }).then(() => {
            // Recargar la página para actualizar la tabla de citas
            window.location.reload();
        });
    }
}