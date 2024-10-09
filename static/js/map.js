// Galería
function openModal(id) {
    document.getElementById(id).style.display = 'block';
    document.body.classList.add('no-scroll'); // Deshabilitar scroll al abrir el modal
}

function closeModal() {
    var modals = document.querySelectorAll('.lightbox');
    modals.forEach(function(modal) {
        modal.style.display = 'none';
    });
    document.body.classList.remove('no-scroll'); // Habilitar scroll al cerrar el modal
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

// descargar app

// Obtener el modal
var modal = document.getElementById("myModal");

// Obtener el botón que abre el modal
var btn = document.getElementById("openModal");

// Obtener el elemento <span> que cierra el modal
var span = document.getElementsByClassName("close")[0];

// Cuando el usuario hace clic en el botón, se abre el modal y se deshabilita el scroll
btn.onclick = function(event) {
    event.preventDefault(); // Prevenir la acción por defecto del enlace
    modal.style.display = "block";
    document.body.classList.add("no-scroll");
}

// Cuando el usuario hace clic en <span> (x), se cierra el modal y se habilita el scroll
span.onclick = function() {
    modal.style.display = "none";
    document.body.classList.remove("no-scroll");
}

// Cuando el usuario hace clic en cualquier parte fuera del modal, se cierra y se habilita el scroll
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        document.body.classList.remove("no-scroll");
    }
}


// ServicIOS
$(document).ready(function() {
    var $section = $('.service_section');
    var sectionOffset = $section.offset().top; // Obtener la posición de la sección
    var shown = false; // Variable para controlar si la sección está visible

    $(window).on('scroll', function() {
        var scrollTop = $(this).scrollTop(); // Posición actual del scroll

        // Verificar si el scroll está en la sección
        if (scrollTop + $(window).height() > sectionOffset && !shown) {
            shown = true; // Marcar como mostrado
            $section.addClass('visible'); // Agregar clase para mostrar
        } else if (scrollTop + $(window).height() <= sectionOffset && shown) {
            shown = false; // Marcar como oculto
            $section.removeClass('visible'); // Quitar clase para ocultar
        }
    });
});