// galeria
function openModal(id) {
    document.getElementById(id).style.display = 'block';
}

function closeModal() {
    var modals = document.querySelectorAll('.lightbox');
    modals.forEach(function(modal) {
        modal.style.display = 'none';
    });
}
// mapa
function toggleMap() {
    const map = document.getElementById('map');
    if (map.style.display === 'none') {
        map.style.display = 'block'; // Muestra el mapa
    } else {
        map.style.display = 'none'; // Oculta el mapa
    }
}

