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

// Variables
let gridInstance = null;
let selectedMedicalHistoryId = null;
const btnAddRecipe = document.getElementById('btn-add-recipe'); // Botón de añadir receta

// Función para cargar los datos de los historiales médicos
const loadMedicalHistories = async () => {
    try {
        const response = await fetch('/core/load_medical_histories/', {
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
                    { name: 'ID', width: '85px' },
                    { name: 'Paciente', width: '250px' },
                    { name: 'Diagnóstico', width: '400px' },
                    { name: 'Tratamiento', width: '400px' },
                    { name: 'Fecha de Creación', width: '200px' },
                    { name: 'Estado', width: '150px' },
                ],
                data: data.medical_histories.map(history => {
                    return [
                        history.id,
                        history.patient,
                        history.diagnosis,
                        history.treatment || 'N/A',
                        history.created_at,
                        history.status,
                    ];
                }),
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
                        results: () => 'registros'
                    },
                    loading: 'Cargando...',
                    noRecordsFound: 'No se encontraron registros coincidentes',
                    error: 'Ocurrió un error al cargar los datos'
                }
            });

            // Evento para manejar la selección de fila
            gridInstance.on('rowClick', (event) => {
                const rowElement = event.target.closest('.gridjs-tr');
                if (!rowElement) return;

                const isAlreadySelected = rowElement.classList.contains('table-active');

                if (isAlreadySelected) {
                    rowElement.classList.remove('table-active');
                    selectedMedicalHistoryId = null;

                    document.getElementById('btn-edit').disabled = true;
                    document.getElementById('btn-delete').disabled = true;
                    btnAddRecipe.disabled = true; // Deshabilitar botón de receta
                    return;
                }

                document.querySelectorAll('.gridjs-tr').forEach(r => r.classList.remove('table-active'));
                rowElement.classList.add('table-active');

                const cells = rowElement.querySelectorAll('.gridjs-td');
                selectedMedicalHistoryId = cells[0].textContent;

                document.getElementById('btn-edit').disabled = false;
                document.getElementById('btn-delete').disabled = false;
                btnAddRecipe.disabled = false; // Habilitar botón de receta
            });

            gridInstance.render(document.getElementById("medicalHistoryTable"));
        } else {
            console.log("No se pudo cargar la lista de historiales médicos");
        }
    } catch (error) {
        console.error("Error al cargar los historiales médicos:", error);
    }
};

// Manejadores de eventos para los botones
document.getElementById('btn-edit').addEventListener('click', () => {
    if (selectedMedicalHistoryId) {
        window.location.href = `/core/edit_medical_history/${selectedMedicalHistoryId}/`;
    }
});

document.getElementById('btn-delete').addEventListener('click', async () => {
    if (selectedMedicalHistoryId) {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará el historial médico seleccionado. ¡No podrás revertirla!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const response = await fetch('/core/delete_medical_history/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({ medical_history_id: selectedMedicalHistoryId }),
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

                        await loadMedicalHistories();

                        selectedMedicalHistoryId = null;
                        document.getElementById('btn-edit').disabled = true;
                        document.getElementById('btn-delete').disabled = true;
                        btnAddRecipe.disabled = true; // Deshabilitar botón de receta
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: `Error: ${result.message}`,
                            icon: "error",
                            confirmButtonText: "Aceptar",
                        });
                    }
                } catch (error) {
                    console.error("Error al eliminar el historial médico:", error);
                    Swal.fire({
                        title: "Error",
                        text: "Ocurrió un error al intentar eliminar el historial médico.",
                        icon: "error",
                        confirmButtonText: "Aceptar",
                    });
                }
            }
        });
    }
});

btnAddRecipe.addEventListener('click', () => {
    if (selectedMedicalHistoryId) {
        window.location.href = `/core/create-prescription/${selectedMedicalHistoryId}/`;
    }
});

// Inicialización al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    loadMedicalHistories();
});