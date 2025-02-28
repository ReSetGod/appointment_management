const loadInitialValues = async (specialityId, doctorId, appointmentDate, appointmentTime) => {
    try {
        // Cargar especialidades
        await listSpecialities(specialityId);

        // Cargar doctores asociados a la especialidad seleccionada
        if (specialityId) {
            await listDoctors(specialityId, doctorId);
        }

        // Configurar fecha
        if (appointmentDate) {
            dateSelect.value = appointmentDate;

            // Cargar horarios solo si doctorId y fecha están disponibles
            if (doctorId && appointmentTime) {
                await listAvailableTimes(doctorId, appointmentDate, appointmentTime);
            }
        }
    } catch (error) {
        console.log("Error al cargar valores iniciales:", error);
    }
};

const listDoctors = async (specialityId, selectedDoctorId = null) => {
    try {
        const response = await fetch(`/core/doctors/${specialityId}`);
        const data = await response.json();
        
        if (data.message === "Success") {
            let options = '<option value="">Seleccione un doctor</option>';
            data.doctors.forEach((doctor) => {
                options += `<option value='${doctor.id}' ${doctor.id == selectedDoctorId ? 'selected' : ''}>${doctor.first_name} ${doctor.last_name}</option>`;
            });
            doctorSelect.innerHTML = options;
        } else {
            doctorSelect.innerHTML = '<option>No hay doctores disponibles</option>';
        }
    } catch (error) {
        console.log(error);
    }
};

const listSpecialities = async (selectedSpecialityId = null) => {
    try {
        const response = await fetch("/core/specialities");
        const data = await response.json();
        
        if (data.message === "Success") {
            let options = '<option value="">Seleccione una especialidad</option>';
            data.specialities.forEach((speciality) => {
                options += `<option value='${speciality.id}' ${speciality.id == selectedSpecialityId ? 'selected' : ''}>${speciality.name}</option>`;
            });
            specialitySelect.innerHTML = options;
        }
    } catch (error) {
        console.log(error);
    }
};

const listAvailableTimes = async (doctorId, date, selectedTime = null) => {
    try {
        // Construir la URL con el horario seleccionado como parámetro
        let url = `/core/available_times/${doctorId}/${date}`;
        if (selectedTime) {
            url += `?selected_time=${selectedTime}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.message === "Success" && data.available_times.length > 0) {
            let options = '<option value="">Seleccione un horario</option>';

            data.available_times.forEach((time) => {
                options += `<option value='${time}' ${
                    time === selectedTime ? "selected" : ""
                }>${time}</option>`;
            });

            timeSelect.innerHTML = options;
        } else {
            timeSelect.innerHTML = '<option value="">No existen horarios disponibles</option>';
        }
    } catch (error) {
        console.log("Error al listar horarios:", error);
    }
};

let initialFormValues = {};

// Función para guardar los valores iniciales del formulario
const saveInitialValues = () => {
    initialFormValues = {
        speciality: specialitySelect.value,
        doctor: doctorSelect.value,
        date: dateSelect.value,
        time: timeSelect.value,
        reason: document.getElementById("exampleFormControlTextarea1").value // Agregar el valor del motivo
    };
};

// Función para verificar si hay cambios en el formulario
const isFormChanged = () => {
    return (
        specialitySelect.value !== initialFormValues.speciality ||
        doctorSelect.value !== initialFormValues.doctor ||
        dateSelect.value !== initialFormValues.date ||
        timeSelect.value !== initialFormValues.time ||
        document.getElementById("exampleFormControlTextarea1").value !== initialFormValues.reason // Verificar si el motivo ha cambiado
    );
};

// Función para activar o desactivar el botón
const updateSaveButtonState = () => {
    const saveButton = document.getElementById("saveButton");
    if (isFormChanged()) {
        saveButton.disabled = false;
    } else {
        saveButton.disabled = true;
    }
};


const initialLoad = async () => {
    // Cargar valores iniciales
    const savedSpecialityId = specialitySelect.dataset.savedSpecialityId;
    const savedDoctorId = doctorSelect.dataset.savedDoctorId;
    const savedAppointmentDate = dateSelect.dataset.savedAppointmentDate;
    const savedAppointmentTime = timeSelect.dataset.savedAppointmentTime;

    await loadInitialValues(savedSpecialityId, savedDoctorId, savedAppointmentDate, savedAppointmentTime);

    // Guardar valores iniciales
    saveInitialValues();

    // Listener para verificar cambios
    specialitySelect.addEventListener("change", async (event) => {
        const specialityId = event.target.value;
    
        // Reiniciar los campos dependientes
        doctorSelect.innerHTML = '<option value="">Seleccione un doctor</option>';
    
        if (specialityId) {
            try {
                // Cargar los doctores asociados a la especialidad seleccionada
                await listDoctors(specialityId);
    
                // Habilitar el campo de doctor si hay opciones disponibles
                if (doctorSelect.options.length > 1) {
                    doctorSelect.disabled = false;
                } else {
                    doctorSelect.disabled = true;
                }
            } catch (error) {
                console.log("Error al cargar doctores:", error);
                doctorSelect.innerHTML = '<option>No hay doctores disponibles</option>';
            }
        } else {
            // Deshabilitar campos dependientes si no se selecciona especialidad
            doctorSelect.disabled = true;
            timeSelect.disabled = true;
        }
    
        // Actualizar el estado del botón de guardar
        updateSaveButtonState();
    });
    
    doctorSelect.addEventListener("change", async () => {
        const doctorId = doctorSelect.value;
        const selectedDate = dateSelect.value;
    
        if (doctorId && selectedDate) {
            await listAvailableTimes(doctorId, selectedDate);
        } else {
            timeSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        }
        updateSaveButtonState();
    });
    
    dateSelect.addEventListener("change", async () => {
        const doctorId = doctorSelect.value;
        const selectedDate = dateSelect.value;
    
        if (doctorId && selectedDate) {
            await listAvailableTimes(doctorId, selectedDate);
        } else {
            timeSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        }
        updateSaveButtonState();
    });

    timeSelect.addEventListener("change", () => {
        updateSaveButtonState();
    });

    document.getElementById("exampleFormControlTextarea1").addEventListener("input", updateSaveButtonState);
};

window.addEventListener("load", async () => {
    await initialLoad();
});