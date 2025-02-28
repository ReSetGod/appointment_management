document.addEventListener("DOMContentLoaded", function () {
  const colors = [
    "#FF6384",
    "#36A2EB",
    "#FFCE56",
    "#4BC0C0",
    "#9966FF",
    "#FF9F40",
    "#4DDBFF",
    "#FFD700",
    "#90EE90",
    "#FF69B4",
  ];

  const chartConfigs = {
    patientConcurrence: {
      type: "line",
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Concurrencia de Pacientes",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
          },
        },
      },
    },
    specialities: {
      type: "bar",
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Especialidades Más Solicitadas",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
          },
        },
      },
    },
    diseases: {
      type: "doughnut",
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Enfermedades Más Recurrentes",
          },
        },
      },
    },
    doctorRatings: {
      type: "bar",
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Calificación Promedio por Doctor",
          },
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 5,
            ticks: {
              stepSize: 1,
              callback: function (value) {
                return value + " ★";
              },
            },
          },
        },
      },
    },
  };

  // Guardar instancias de Chart.js
  const charts = {};

  async function createChart(endpoint, elementId, config, timeFrame = "30") {
    try {
      const response = await fetch(
        `/reports/${endpoint}/?time_frame=${timeFrame}`
      );
      if (!response.ok) throw new Error("Network response was not ok");

      const jsonData = await response.json();
      if (!jsonData.success) throw new Error(jsonData.error);

      const ctx = document.getElementById(elementId).getContext("2d");

      // Destruir la instancia de Chart.js si ya existe
      if (charts[elementId]) {
        charts[elementId].destroy();
      }

      const chartData = {
        labels: jsonData.data.labels,
        datasets: [
          {
            label: config.type === "line" ? "Cantidad de Pacientes" : "Total",
            data: jsonData.data.data,
            backgroundColor:
              config.type === "bar"
                ? colors.slice(0, jsonData.data.labels.length)
                : config.type === "doughnut"
                ? colors.slice(0, jsonData.data.labels.length)
                : "#0077B6",
            borderColor: config.type === "line" ? "#0077B6" : "white",
            borderWidth: 1,
          },
        ],
      };

      charts[elementId] = new Chart(ctx, {
        type: config.type,
        data: chartData,
        options: config.options,
      });
    } catch (error) {
      console.error("Error loading chart:", error);
      document.getElementById(elementId).innerHTML =
        "Error al cargar los datos";
    }
  }

  // Inicializar los gráficos
  createChart(
    "patient-concurrence",
    "patientConcurrenceChart",
    chartConfigs.patientConcurrence
  );
  createChart(
    "most-requested-specialities",
    "specialitiesChart",
    chartConfigs.specialities
  );
  createChart(
    "most-recurrent-diseases",
    "diseasesChart",
    chartConfigs.diseases
  );
  createChart(
    "doctor-ratings",
    "doctorRatingsChart",
    chartConfigs.doctorRatings
  );

  // Guardar los marcos de tiempo activos
  const activeTimeFrames = {
    patientConcurrenceChart: "30",
    specialitiesChart: "30",
    diseasesChart: "30",
  };

  // Función para formatear el marco de tiempo
  function formatTimeFrame(days) {
    switch (days) {
      case "30":
        return "Últimos 30 días";
      case "90":
        return "Últimos 3 meses";
      case "180":
        return "Últimos 6 meses";
      case "365":
        return "Último año";
      default:
        return `Últimos ${days} días`;
    }
  }

  // Añadir event listeners para los botones de filtro de tiempo
  document.querySelectorAll(".time-filter").forEach((button) => {
    button.addEventListener("click", function () {
      const timeFrame = this.dataset.timeFrame;
      const chartId =
        this.closest(".chart-container").querySelector("canvas").id;
      const config = chartConfigs[chartId.replace("Chart", "")];

      // Actualizar el tiempo activo
      activeTimeFrames[chartId] = timeFrame;

      // Actualizar el botón activo
      this.closest(".chart-container")
        .querySelectorAll(".time-filter")
        .forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // Mapear los endpoints con los IDs de los gráficos
      const endpointMap = {
        patientConcurrenceChart: "patient-concurrence",
        specialitiesChart: "most-requested-specialities",
        diseasesChart: "most-recurrent-diseases",
      };

      // Refrescar el gráfico
      createChart(endpointMap[chartId], chartId, config, timeFrame);
    });
  });

  // Funciones para exportar gráficos a imagen y PDF
  function exportToImage(chartId) {
    const canvas = document.getElementById(chartId);
    const image = canvas.toDataURL("image/png");
    const link = document.createElement("a");
    link.download = `${chartId}.png`;
    link.href = image;
    link.click();
  }

  function exportToPDF(chartId) {
    const canvas = document.getElementById(chartId);
    const image = canvas.toDataURL("image/png");

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF("landscape");

    // Obtener el título y el marco de tiempo
    const chartContainer = canvas.closest(".chart-container");
    const title = chartContainer.querySelector("h2").textContent;
    const timeFrame = formatTimeFrame(activeTimeFrames[chartId]);

    // Añadir título y marco de tiempo al PDF
    pdf.setFontSize(16);
    pdf.text(title, 15, 15);
    pdf.setFontSize(12);
    pdf.text(timeFrame, 15, 25);

    // Añadir la imagen al PDF
    const imgProps = pdf.getImageProperties(image);
    const pdfWidth = pdf.internal.pageSize.getWidth() - 30;
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
    pdf.addImage(image, "PNG", 15, 35, pdfWidth, pdfHeight);

    pdf.save(`${chartId}.pdf`);
  }

  // Añadir event listeners para los botones de exportar
  document.querySelectorAll(".export-img").forEach((button) => {
    button.addEventListener("click", function () {
      const chartId = this.dataset.chart;
      exportToImage(chartId);
    });
  });

  document.querySelectorAll(".export-pdf").forEach((button) => {
    button.addEventListener("click", function () {
      const chartId = this.dataset.chart;
      exportToPDF(chartId);
    });
  });
});
