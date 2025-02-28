// Función para obtener el token CSRF
const getCookie = (name) => {
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
};

// Variable para almacenar la instancia de Grid.js
let gridInstance = null;

// Función para cargar el historial de citas
const loadAppointmentHistory = async (patientId = null) => {
    try {
        const url = patientId 
            ? `/core/load_appointment_history/?patient_id=${patientId}` 
            : '/core/load_appointment_history/';

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.message === "Success") {
            // Si ya hay una instancia de Grid.js, destruirla antes de crear una nueva
            if (gridInstance) {
                gridInstance.destroy();
                gridInstance = null;
            }

            // Crear una nueva instancia de Grid.js
            gridInstance = new gridjs.Grid({
                columns: [
                    { name: 'ID', width: '90px' },
                    { name: 'Fecha', width: '175px' },
                    'Horario',
                    'Doctor',
                    'Estado',
                    {
                        name: 'Acciones',
                        sort: false,
                        width: '150px',
                        formatter: (cell, row) => {
                            return gridjs.h('button', {
                                className: 'btn custom-button',
                                onClick: () => viewAppointmentDetails(row.cells[0].data)
                            }, 'Ver Detalles');
                        }
                    }
                ],
                data: data.appointments.map(appointment => [
                    appointment.id,
                    appointment.date,
                    appointment.time,
                    appointment.doctor,
                    appointment.status
                ]),
                pagination: { limit: 5 },
                sort: true,
                search: true,
                language: {
                    'search': { 'placeholder': 'Buscar...' },
                    'pagination': {
                        'previous': 'Anterior',
                        'next': 'Siguiente',
                        'showing': 'Mostrando',
                        'to': 'a',
                        'of': 'de',
                        'results': () => 'citas'
                    },
                    'loading': 'Cargando...',
                    'noRecordsFound': 'No se encontraron citas',
                    'error': 'Ocurrió un error al cargar los datos'
                }
            });

            // Renderizar Grid.js en el elemento deseado
            document.getElementById("appointmentHistoryTable").innerHTML = "";
            gridInstance.render(document.getElementById("appointmentHistoryTable"));

        } else {
            console.log("No se pudo cargar el historial de citas");
        }

    } catch (error) {
        console.log("Error al cargar el historial de citas:", error);
    }
};

// Función para buscar pacientes
const searchPatients = async (query) => {
    try {
        const response = await fetch(`/core/search_patients?query=${query}`);
        const data = await response.json();
        return data.patients.map(patient => ({
            id: patient.id,
            text: `${patient.first_name} ${patient.last_name} - ${patient.identification}`
        }));
    } catch (error) {
        console.error('Error fetching patients:', error);
        return [];
    }
};

// Configurar búsqueda de pacientes
const setupPatientSearch = () => {
    const patientInput = document.getElementById('patientSearch');
    if (!patientInput) return;

    const tomSelect = new TomSelect(patientInput, {
        valueField: 'id',
        labelField: 'text',
        searchField: 'text',
        load: async (query, callback) => {
            if (query.length < 3) return callback();
            const results = await searchPatients(query);
            callback(results);
        },
        placeholder: 'Buscar paciente...',
        maxOptions: 5,
        allowEmptyOption: false,
        render: {
            no_results: function () {
                return '<div class="no-results">No se encontraron pacientes.</div>';
            },
        },
    });

    const loadAppointmentsButton = document.createElement('button');
    loadAppointmentsButton.textContent = 'Cargar Citas';
    loadAppointmentsButton.classList.add('btn', 'custom-button', 'mt-2');
    loadAppointmentsButton.style.display = 'none';

    loadAppointmentsButton.addEventListener('click', () => {
        const selectedValue = tomSelect.getValue();
        if (selectedValue) {
            loadAppointmentHistory(selectedValue);
        }
    });

    patientInput.parentNode.appendChild(loadAppointmentsButton);

    tomSelect.on('change', () => {
        const selectedValue = tomSelect.getValue();
        loadAppointmentsButton.style.display = selectedValue ? 'block' : 'none';
    });
};

// Función para mostrar el modal con detalles de la cita
function viewAppointmentDetails(appointmentId, isHistory = true) {
    const url = `/core/appointment/${appointmentId}/details/?is_history=${isHistory}`;

    fetch(url)
        .then(response => response.text())
        .then(html => {
            const modalBody = document.getElementById('history-modal-body');
            if (modalBody) {
                modalBody.innerHTML = html;
                const modal = new bootstrap.Modal(document.getElementById('appointmentHistoryDetailsModal'));
                modal.show();
            } else {
                console.error('No se pudo encontrar el cuerpo del modal para mostrar los detalles.');
            }
        })
        .catch(error => console.error('Error al cargar detalles de la cita:', error));
}

// Inicialización al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    setupPatientSearch();
    loadAppointmentHistory();
});