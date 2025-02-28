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

// Función para cargar el historial de diagnósticos
const loadDiagnosticsHistory = async (patientId = null) => {
    try {
        const url = patientId 
            ? `/core/diagnostics-history/?patient_id=${patientId}` 
            : '/core/diagnostics-history/';

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
                    { name: 'Diagnóstico', width: '400px' },
                    'Doctor',
                    {
                        name: 'Acciones',
                        sort: false,
                        width: '150px',
                        formatter: (cell, row) => {
                            return gridjs.h('button', {
                                className: 'btn custom-button',
                                onClick: () => viewDiagnosticDetails(row.cells[0].data)
                            }, 'Ver Detalles');
                        }
                    }
                ],
                data: data.diagnostics.map(diagnostic => [
                    diagnostic.id,
                    diagnostic.created_at,
                    diagnostic.diagnosis,
                    diagnostic.doctor
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
                        'results': () => 'diagnósticos'
                    },
                    'loading': 'Cargando...',
                    'noRecordsFound': 'No se encontraron diagnósticos',
                    'error': 'Ocurrió un error al cargar los datos'
                }
            });

            // Renderizar Grid.js en el elemento deseado
            document.getElementById("diagnosticsHistoryTable").innerHTML = "";
            gridInstance.render(document.getElementById("diagnosticsHistoryTable"));

        } else {
            console.log("No se pudo cargar el historial de diagnósticos");
        }

    } catch (error) {
        console.log("Error al cargar el historial de diagnósticos:", error);
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

    const loadDiagnosticsButton = document.createElement('button');
    loadDiagnosticsButton.textContent = 'Cargar Diagnósticos';
    loadDiagnosticsButton.classList.add('btn', 'custom-button', 'mt-2');
    loadDiagnosticsButton.style.display = 'none';

    loadDiagnosticsButton.addEventListener('click', () => {
        const selectedValue = tomSelect.getValue();
        if (selectedValue) {
            loadDiagnosticsHistory(selectedValue);
        }
    });

    patientInput.parentNode.appendChild(loadDiagnosticsButton);

    tomSelect.on('change', () => {
        const selectedValue = tomSelect.getValue();
        loadDiagnosticsButton.style.display = selectedValue ? 'block' : 'none';
    });
};

// Función para mostrar el modal con detalles del diagnóstico
function viewDiagnosticDetails(diagnosticId) {
    const url = `/core/diagnostic/${diagnosticId}/details/`;

    fetch(url)
        .then(response => response.text())
        .then(html => {
            const modalBody = document.getElementById('diagnostics-modal-body');
            if (modalBody) {
                modalBody.innerHTML = html;
                const modal = new bootstrap.Modal(document.getElementById('diagnosticDetailsModal'));
                modal.show();
            } else {
                console.error('No se pudo encontrar el cuerpo del modal para mostrar los detalles.');
            }
        })
        .catch(error => console.error('Error al cargar detalles del diagnóstico:', error));
}

// Inicialización al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    setupPatientSearch();
    loadDiagnosticsHistory();
});