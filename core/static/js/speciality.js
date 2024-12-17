// Función para cargar las especialidades basadas en la búsqueda
const loadSpecialities = async (query = "") => {
    try {
        // Realizamos la solicitud a la API con el parámetro de búsqueda
        const response = await fetch(`/core/specialities?search=${query}`);
        const data = await response.json();

        if (data.message === "Success") {
            const specialityContainer = document.getElementById("specialityContainer");
            specialityContainer.innerHTML = ""; // Limpiar el contenedor antes de agregar los elementos

            // Crear las tarjetas de especialidad dinámicamente
            data.specialities.forEach(speciality => {
                const card = document.createElement("div");
                card.classList.add("card");
                
                // Contenido de la tarjeta
                card.innerHTML = `
                    <h6 class="title">${speciality.name}</h6>
                    <h6 class="amount">${speciality.description}</h6>
                    <div class="badge">
                        <span class="text-success-bg">Detalles</span>
                    </div>
                `;

                // Evento de clic para redirigir a la página de detalle de la especialidad
                card.addEventListener("click", () => {
                    window.location.href = `/core/specialities/${speciality.id}/`; // URL de la página de detalle
                });

                specialityContainer.appendChild(card);
            });
        } else {
            // Mostrar un mensaje si no se encuentran especialidades
            specialityContainer.innerHTML = "<p>No se encontraron especialidades.</p>";
        }
    } catch (error) {
        console.error("Error al cargar las especialidades:", error);
    }
};

// Función para manejar la escritura en el campo de búsqueda
const handleSearch = (event) => {
    const query = event.target.value.trim().toLowerCase();
    loadSpecialities(query);

    // Mostrar u ocultar el botón de borrar
    const clearSearch = document.getElementById("clear-search");
    clearSearch.style.display = query ? "inline" : "none";
};

// Función para limpiar el campo de búsqueda y recargar todas las especialidades
const clearSearchField = () => {
    const searchInput = document.getElementById("search-input");
    searchInput.value = ""; // Vaciar el campo de búsqueda
    document.getElementById("clear-search").style.display = "none"; // Ocultar el botón "X"
    loadSpecialities(); // Recargar todas las especialidades
};

// Inicializar la carga de especialidades y agregar el listener al campo de búsqueda
const initialLoad = () => {
    loadSpecialities(); // Cargar todas las especialidades al inicio

    const searchInput = document.getElementById("search-input");
    const clearSearch = document.getElementById("clear-search");

    // Agregar eventos al campo de búsqueda y al botón "X"
    searchInput.addEventListener("input", handleSearch);
    clearSearch.addEventListener("click", clearSearchField);
};

window.addEventListener("load", initialLoad);