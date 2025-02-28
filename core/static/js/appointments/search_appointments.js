const searchAppointments = async (query = '') => {
    try {
        const response = await fetch(`/core/search_attended_appointments?query=${query}`);
        const data = await response.json();
        return data.appointments.map(appointment => ({
            id: appointment.id,
            text: appointment.text
        }));
    } catch (error) {
        console.error('Error fetching appointments:', error);
        return [];
    }
};

const setupAppointmentSearch = async () => {
    const appointmentInput = document.getElementById('appointmentSearch');
    if (!appointmentInput) {
        console.log('Elemento de búsqueda no encontrado.');
        return;
    }

    // Cargar citas iniciales.
    const initialResults = await searchAppointments(); // Sin query al inicio.

    new TomSelect(appointmentInput, {
        valueField: 'id',
        labelField: 'text',
        searchField: 'text',
        options: initialResults, // Opciones iniciales.
        load: async (query, callback) => {
            if (query.length < 3) {
                return callback();
            }
            const results = await searchAppointments(query);
            callback(results);
        },
        placeholder: 'Buscar cita...',
        maxOptions: 10,
        allowEmptyOption: false,
        render: {
            no_results: function () {
                return '<div class="no-results">No se encontraron citas.</div>';
            },
        },
    });
};

document.addEventListener('DOMContentLoaded', setupAppointmentSearch);