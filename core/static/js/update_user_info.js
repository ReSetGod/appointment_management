document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("configurationForm");
    const submitButton = document.getElementById("submitButton");

    // Inicialmente deshabilitar el botón
    submitButton.disabled = true;

    // Detectar cambios en cualquier campo del formulario
    form.addEventListener("input", () => {
        submitButton.disabled = false; // Habilitar el botón si hay algún cambio
    });

    // Manejar el envío del formulario
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(form);

        try {
            // Enviar datos al servidor
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });

            const data = await response.json();

            if (response.ok && data.success) {
                window.location.reload(); // Recargar la página para mostrar los cambios
            } else if (data.errors) {
                alert("Error al actualizar. Revisa los campos.");
                console.error("Errores del formulario:", data.errors);
            } else {
                alert("Error inesperado. Por favor, intenta de nuevo.");
            }
        } catch (error) {
            console.error("Error al enviar el formulario:", error);
            alert("Ocurrió un error al enviar los datos.");
        } finally {
            submitButton.disabled = true; // Deshabilitar el botón después del envío
        }
    });
});