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

// Variable para almacenar la fila seleccionada
let selectedPatientId = null;

// Función para cargar los datos de los pacientes
const loadPatients = async () => {
    try {
        const response = await fetch('/core/load_patients/', {
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
            if (gridInstance) {
                gridInstance.destroy();
                gridInstance = null;
            }

            gridInstance = new gridjs.Grid({
                columns: [
                    { name: 'ID', width: '85px'},
                    { name: 'Nombre Completo', width: '350px' },
                    { name: 'Identificación', width: '200px' },
                    { name: 'Teléfono', width: '150px' },
                    { name: 'Dirección', width: '200px' },
                    { name: 'Ciudad', width: '150px' },
                    { name: 'Fecha de Nacimiento', width: '240px' },
                    'Género',
                ],
                data: data.patients.map(patient => [
                    patient.id,
                    patient.name,
                    patient.identification,
                    patient.phone_number,
                    patient.address,
                    patient.city,
                    patient.birth_date,
                    patient.genre,
                ]),
                pagination: { limit: 10 },
                sort: true,
                search: true,
                style: {
                    table: {
                        cursor: 'pointer'
                    }
                },
                language: {
                    search: { placeholder: 'Buscar...' },
                    pagination: {
                        previous: 'Anterior',
                        next: 'Siguiente',
                        showing: 'Mostrando',
                        to: 'a',
                        of: 'de',
                        results: () => 'pacientes'
                    },
                    loading: 'Cargando...',
                    noRecordsFound: 'No se encontraron registros coincidentes',
                    error: 'Ocurrió un error al cargar los datos'
                }
            });

            // Evento para manejar la selección de fila
            gridInstance.on('rowClick', (event) => {
                try {
                    const target = event.target;
                    const rowElement = target.closest('.gridjs-tr');
                    if (!rowElement) return;

                    const isAlreadySelected = rowElement.classList.contains('table-active');

                    // Si ya está seleccionada, deseleccionar
                    if (isAlreadySelected) {
                        rowElement.classList.remove('table-active');
                        selectedPatientId = null;

                        // Deshabilitar botones
                        document.getElementById('btn-edit').disabled = true;
                        document.getElementById('btn-delete').disabled = true;

                        return;
                    }

                    // Si no está seleccionada, seleccionar la nueva fila
                    document.querySelectorAll('.gridjs-tr').forEach(r => r.classList.remove('table-active'));
                    rowElement.classList.add('table-active');

                    const cells = rowElement.querySelectorAll('.gridjs-td');
                    const rowData = Array.from(cells).map(cell => cell.textContent);

                    // Obtener el valor del ID (primera columna, aunque esté oculta)
                    selectedPatientId = rowData[0];

                    // Habilitar botones
                    document.getElementById('btn-edit').disabled = false;
                    document.getElementById('btn-delete').disabled = false;

                } catch (error) {
                    console.error("Error al manejar el evento de clic en la fila:", error);
                }
            });
            gridInstance.render(document.getElementById("patientTable"));
        } else {
            console.log("No se pudo cargar la lista de pacientes");
        }
    } catch (error) {
        console.error("Error al cargar los pacientes:", error);
    }
};

// Manejadores de eventos para los botones
document.getElementById('btn-edit').addEventListener('click', () => {
    if (selectedPatientId) {
        const editUrl = `/core/edit_patient/${selectedPatientId}/`;
        window.location.href = editUrl;
    }
});

document.getElementById('btn-delete').addEventListener('click', async () => {
    if (selectedPatientId) {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará al paciente seleccionado. ¡No podrás revertirla!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const response = await fetch('/core/delete_patient/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({ patient_id: selectedPatientId }),
                    });

                    const result = await response.json();

                    if (response.ok) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: result.message,
                            icon: "success",
                            confirmButtonText: "Aceptar",
                            confirmButtonColor: "#3085d6",
                        });

                        // Recargar la tabla después de eliminar
                        await loadPatients();

                        // Restablecer estado de botones y paciente seleccionado
                        selectedPatientId = null;
                        document.getElementById('btn-edit').disabled = true;
                        document.getElementById('btn-delete').disabled = true;
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: `Error: ${result.message}`,
                            icon: "error",
                            confirmButtonText: "Aceptar",
                        });
                    }
                } catch (error) {
                    console.error("Error al eliminar el paciente:", error);
                    Swal.fire({
                        title: "Error",
                        text: "Ocurrió un error al intentar eliminar el paciente.",
                        icon: "error",
                        confirmButtonText: "Aceptar",
                    });
                }
            }
        });
    } else {
        Swal.fire({
            title: "Advertencia",
            text: "Por favor, selecciona un paciente para eliminar.",
            icon: "warning",
            confirmButtonText: "Aceptar",
        });
    }
});

// Inicialización al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    loadPatients();
});