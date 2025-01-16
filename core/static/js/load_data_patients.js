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

const setupPatientSearch = () => {
    const patientInput = document.getElementById('patientSearch');
    if (!patientInput) return;

    // Inicializa TomSelect
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

    // Añade el botón para cargar citas
    const loadAppointmentsButton = document.createElement('button');
    loadAppointmentsButton.textContent = 'Cargar Citas';
    loadAppointmentsButton.classList.add('btn', 'btn-primary', 'mt-2');
    loadAppointmentsButton.style.display = 'none'; // Solo muestra cuando se selecciona un paciente

    // Agrega los atributos HTMX
    loadAppointmentsButton.setAttribute('hx-get', '/core/future_appointments');
    loadAppointmentsButton.setAttribute('hx-include', '#patientSearch');
    loadAppointmentsButton.setAttribute('hx-target', '#posts tbody');
    loadAppointmentsButton.setAttribute('hx-swap', 'outerHTML');

    // Inserta el botón después del selector
    patientInput.parentNode.appendChild(loadAppointmentsButton);

    // Muestra el botón cuando se selecciona un paciente
    tomSelect.on('change', () => {
        const selectedValue = tomSelect.getValue();
        loadAppointmentsButton.style.display = selectedValue ? 'block' : 'none';
    });
};

document.addEventListener('DOMContentLoaded', setupPatientSearch);