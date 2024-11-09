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

const loadDiagnosticsHistory = async () => {
    try {
        const response = await fetch('/core/diagnostics-history/', {
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
            // Crear la tabla usando Grid.js
            const grid = new gridjs.Grid({
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
                                onClick: () => viewDiagnosticDetails(row.cells[0].data) // Usar el ID para los detalles
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
                pagination: {
                    limit: 5
                },
                sort: true,
                search: true,
                language: {
                    'search': {
                        'placeholder': 'Buscar...'
                    },
                    'pagination': {
                        'previous': 'Anterior',
                        'next': 'Siguiente',
                        'showing': 'Mostrando',
                        'to': 'a',  
                        'of': 'de',
                        'results': () => 'diagnósticos'
                    },
                    'loading': 'Cargando...',
                    'noRecordsFound': 'No se encontraron registros coincidentes', 
                    'error': 'Ocurrió un error al cargar los datos'
                }
            });

            // Renderizar Grid.js en el elemento deseado
            grid.render(document.getElementById("diagnosticsHistoryTable"));

        } else {
            console.log("No se pudo cargar el historial de diagnósticos");
        }

    } catch (error) {
        console.log("Error al cargar el historial de diagnósticos:", error);
    }
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
                
                // Mostrar el nuevo modal usando Bootstrap 5 sin jQuery
                const modal = new bootstrap.Modal(document.getElementById('diagnosticDetailsModal'));
                modal.show();
            } else {
                console.error('No se pudo encontrar el cuerpo del modal para mostrar los detalles.');
            }
        })
        .catch(error => console.error('Error al cargar detalles del diagnóstico:', error));
}

// Ejecutar la función al cargar la página
window.addEventListener("load", () => {
    loadDiagnosticsHistory();
});