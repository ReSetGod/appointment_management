document.addEventListener("DOMContentLoaded", function () {
    const password1 = document.getElementById("id_password1");
    const password2 = document.getElementById("id_password2");
    const errorContainer = document.getElementById("password-error");

    password2.addEventListener("input", function () {
        if (password1.value !== password2.value) {
            errorContainer.style.display = "block";
        } else {
            errorContainer.style.display = "none";
        }
    });

    password1.addEventListener("input", function () {
        if (password2.value && password1.value !== password2.value) {
            errorContainer.style.display = "block";
        } else {
            errorContainer.style.display = "none";
        }
    });

    // Mostrar mensajes desde Django usando JavaScript
    const messagesContainer = document.getElementById("django-messages-container");
    if (messagesContainer) {
        const messages = messagesContainer.querySelectorAll("div[data-message-text]");
        messages.forEach(msg => {
            const text = msg.getAttribute("data-message-text");
            const tag = msg.getAttribute("data-message-tag");

            Swal.fire({
                icon: tag === "success" ? "success" : "error",
                title: tag === "success" ? "¡Éxito!" : "Error",
                text: text,
                confirmButtonText: 'OK',
                confirmButtonColor: '#0077B6'
            });
        });
    }
});