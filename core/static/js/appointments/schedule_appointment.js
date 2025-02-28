const listDoctors = async (specialityId) => {
    try {
        const response = await fetch(`/core/doctors/${specialityId}`);
        const data = await response.json();
        
        if (data.message === "Success") {
            let options = '<option value="">Seleccione un doctor</option>';
            data.doctors.forEach((doctor) => {
                options += `<option value='${doctor.id}'>${doctor.first_name} ${doctor.last_name}</option>`;
            });
            doctorSelect.innerHTML = options;
        } else {
            doctorSelect.innerHTML = '<option>No hay doctores disponibles</option>';
        }
        
    } catch (error) {
        console.log(error);
    }
};

const listSpecialities = async () => {
    try {
        const response = await fetch("/core/specialities");
        const data = await response.json();
        
        if (data.message === "Success") {
            let options = '<option value="">Seleccione una especialidad</option>';
            data.specialities.forEach((speciality) => {
                options += `<option value='${speciality.id}'>${speciality.name}</option>`;
            });
            specialitySelect.innerHTML = options;
        }
        
    } catch (error) {
        console.log(error);
    }
};

const listAvailableTimes = async (doctorId, date) => {
    try {
        const response = await fetch(`/core/available_times/${doctorId}/${date}`);
        const data = await response.json();
        
        if (data.message === "Success" && data.available_times.length > 0) {
            let options = '<option value="">Seleccione un horario</option>';
            data.available_times.forEach((time) => {
                options += `<option value='${time}'>${time}</option>`;
            });
            timeSelect.innerHTML = options;
        } else {
            timeSelect.innerHTML = '<option value="">No existen horarios disponibles</option>';
        }
        
    } catch (error) {
        console.log(error);
    }
};

const initialLoad = async () => {
    await listSpecialities();

    doctorSelect.innerHTML = '<option value="">Seleccione un doctor</option>';
    timeSelect.innerHTML = '<option value="">Seleccione un horario</option>';
    dateSelect.disabled = true; // Desactivar el campo de fecha inicialmente

    const checkFormCompletion = () => {
        const specialityId = specialitySelect.value;
        const doctorId = doctorSelect.value;
        if (specialityId && doctorId) {
            dateSelect.disabled = false;
        } else {
            dateSelect.disabled = true;
        }
    };

    // Escucha los cambios en el select de especialidades
    specialitySelect.addEventListener("change", async (event) => {
        const specialityId = event.target.value;
        if (specialityId) {
            await listDoctors(specialityId);
        } else {
            doctorSelect.innerHTML = '<option value="">Seleccione un doctor</option>';
            timeSelect.innerHTML = '<option value="">Seleccione un horario</option>';
            dateSelect.disabled = true;
        }
        checkFormCompletion();
    });

    doctorSelect.addEventListener("change", () => {
        checkFormCompletion();
        const doctorId = doctorSelect.value;
        const selectedDate = dateSelect.value;
        if (doctorId && selectedDate) {
            listAvailableTimes(doctorId, selectedDate);
        }
    });

    dateSelect.addEventListener("change", () => {
        const selectedDate = dateSelect.value;
        const doctorId = doctorSelect.value;
        if (doctorId && selectedDate) {
            listAvailableTimes(doctorId, selectedDate);
        }
    });
};

window.addEventListener("load", async () => {
    await initialLoad();
});