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

    new TomSelect(patientInput, {
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
            no_results:function(){
                return '<div class="no-results">No se encontraron pacientes.</div>';
            },
        },
    });
};

document.addEventListener('DOMContentLoaded', setupPatientSearch);