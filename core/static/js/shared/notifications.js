document.addEventListener('DOMContentLoaded', function() {
    const notificationsToggle = document.querySelector('.notifications-toggle');
    const notificationsDropdown = document.querySelector('.notifications-dropdown');
    
    if (notificationsToggle) {
        notificationsToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationsDropdown.style.display = 
                notificationsDropdown.style.display === 'block' ? 'none' : 'block';
        });
    }

    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        if (notificationsDropdown && !notificationsDropdown.contains(e.target)) {
            notificationsDropdown.style.display = 'none';
        }
    });
});