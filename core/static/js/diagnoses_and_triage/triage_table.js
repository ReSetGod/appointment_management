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

let gridInstance = null;
let selectedTriageId = null;

const loadTriages = async () => {
    try {
        const response = await fetch('/core/load_triages/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();

        if (data.message === "Success") {
            if (gridInstance) {
                gridInstance.destroy();
                gridInstance = null;
            }

            const getCategoryDisplay = (category) => {
                switch(category) {
                    case 'Normal':
                        return '🟢 Normal';
                    case 'Alerta Moderada':
                        return '🟡 Alerta Moderada';
                    case 'Alerta Severa':
                        return '🟠 Alerta Severa';
                    case 'Crítico':
                        return '🔴 Crítico';
                    default:
                        return category;
                }
            };
            
            gridInstance = new gridjs.Grid({
                columns: [
                    { name: 'ID', width: '85px' },
                    { name: 'Paciente', width: '250px' },
                    { name: 'Signos Vitales', width: '300px' },
                    { name: 'Puntaje Total', width: '120px' },
                    { name: 'Categoría', width: '150px' },
                    { name: 'Fecha', width: '200px' },
                ],
                data: data.triages.map(triage => [
                    triage.id,
                    triage.patient_name,
                    `FC: ${triage.heart_rate} | FR: ${triage.respiratory_rate} | PA: ${triage.systolic_blood_pressure} | SpO2: ${triage.oxygen_saturation}%`,
                    triage.total_score,
                    getCategoryDisplay(triage.category),
                    triage.created_at
                ]),
                pagination: { limit: 10 },
                sort: true,
                search: true,
                style: {
                    table: { cursor: 'pointer' }
                },
                language: {
                    search: { placeholder: 'Buscar...' },
                    pagination: {
                        previous: 'Anterior',
                        next: 'Siguiente',
                        showing: 'Mostrando',
                        to: 'a',
                        of: 'de',
                        results: () => 'triajes'
                    }
                }

            });

            gridInstance.on('rowClick', (event) => {
                try {
                    const rowElement = event.target.closest('.gridjs-tr');
                    if (!rowElement) return;
            
                    const isAlreadySelected = rowElement.classList.contains('table-active');
            
                    if (isAlreadySelected) {
                        rowElement.classList.remove('table-active');
                        selectedTriageId = null;
                        document.getElementById('btn-edit').disabled = true;
                        document.getElementById('btn-details').disabled = true;
                        return;
                    }
            
                    document.querySelectorAll('.gridjs-tr').forEach(r => r.classList.remove('table-active'));
                    rowElement.classList.add('table-active');
            
                    const cells = rowElement.querySelectorAll('.gridjs-td');
                    selectedTriageId = cells[0].textContent;
                    document.getElementById('btn-edit').disabled = false;
                    document.getElementById('btn-details').disabled = false;
            
                } catch (error) {
                    console.error("Error al manejar el evento de clic en la fila:", error);
                }
            });

            gridInstance.render(document.getElementById("triageTable"));
        }
    } catch (error) {
        console.error("Error al cargar los triajes:", error);
    }
};

document.getElementById('btn-edit').addEventListener('click', () => {
    if (selectedTriageId) {
        window.location.href = `/core/edit_triage/${selectedTriageId}/`;
    }
});

document.getElementById('btn-details').addEventListener('click', () => {
    if (selectedTriageId) {
        window.location.href = `/core/triage_details/${selectedTriageId}/`;
    }
});

window.addEventListener('DOMContentLoaded', () => {
    loadTriages();
});