document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("configurationForm");
    const submitButton = document.getElementById("submitButton");
    const deleteAccountButton = document.querySelector(".btn-danger"); // Botón de eliminar cuenta
    const deleteAccountForm = document.createElement("form"); // Crear un formulario dinámico para eliminar cuenta

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

    // Manejar el clic en el botón "Eliminar cuenta"
    deleteAccountButton.addEventListener("click", (event) => {
        event.preventDefault(); // Evitar el envío por defecto

        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará tu cuenta y toda tu información asociada. ¡No podrás revertirla!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then((result) => {
            if (result.isConfirmed) {
                // Configurar la acción del formulario dinámico
                deleteAccountForm.method = "POST";
                deleteAccountForm.action = deleteUserUrl; // Usar la URL pasada desde la plantilla
                const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
                deleteAccountForm.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">`;
                document.body.appendChild(deleteAccountForm);
                deleteAccountForm.submit();
            }
        });
    });
});