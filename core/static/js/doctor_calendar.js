document.addEventListener('DOMContentLoaded', function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const calendarEl = document.getElementById('calendar');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día'
        },
        events: '/core/doctor/appointments/',
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        },
        eventClick: function(info) {
            const modal = new bootstrap.Modal(document.getElementById('calendarDetailsModal'));
            
            fetch(`/core/appointment/${info.event.id}/details/?is_calendar=true`)
                .then(response => response.text())
                .then(html => {
                    const modalBody = document.getElementById('calendarDetailsBody');
                    modalBody.innerHTML = html;
                    modal.show();
                    
                    // Remove aria-hidden from wrapper
                    const wrapper = document.querySelector('.wrapper');
                    if (wrapper) {
                        wrapper.removeAttribute('aria-hidden');
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    });

    calendar.render();

    document.body.addEventListener('click', function (event) {
        if (event.target.id === 'markAsAttendedBtn') {
            const button = event.target;
            const appointmentId = button.getAttribute('data-appointment-id');
            const csrftoken = getCookie('csrftoken');

            fetch(`/core/doctor/mark_as_attended/${appointmentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    // Close modal first and restore focus
                    const modal = bootstrap.Modal.getInstance(document.getElementById('calendarDetailsModal'));
                    const wrapper = document.querySelector('.wrapper');
                    if (wrapper) {
                        wrapper.setAttribute('aria-hidden', 'false');
                    }
                    
                    if (modal) {
                        modal.hide();
                        setTimeout(() => {
                            calendar.refetchEvents();
                            Swal.fire({
                                title: '¡Éxito!',
                                text: data.message,
                                icon: 'success',
                                confirmButtonColor: '#0077B6'
                            });
                        }, 150);
                    }
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.message || 'Error al procesar la solicitud',
                        icon: 'error',
                        confirmButtonColor: '#0077B6'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    title: 'Error',
                    text: error.message || 'Ocurrió un error al procesar la solicitud.',
                    icon: 'error',
                    confirmButtonColor: '#0077B6'
                });
            });
        }
    });
});