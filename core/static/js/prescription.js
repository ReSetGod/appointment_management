function downloadPrescription(prescriptionId) {
    
    const url = `/core/download-prescription/${prescriptionId}/`;
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('La receta no está disponible');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `Receta_${prescriptionId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            alert('Error: ' + error.message);
        });
}