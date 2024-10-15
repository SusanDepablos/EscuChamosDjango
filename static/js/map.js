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
        map.style.display = 'block'; 
    } else {
        map.style.display = 'none';
    }
}

// descargar app

var modal = document.getElementById("myModal");

var btn = document.getElementById("openModal");

var span = document.getElementsByClassName("close")[0];

btn.onclick = function(event) {
    event.preventDefault(); 
    modal.style.display = "block";
    document.body.classList.add("no-scroll");
}

span.onclick = function() {
    modal.style.display = "none";
    document.body.classList.remove("no-scroll");
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        document.body.classList.remove("no-scroll");
    }
}

// ServicIOS
$(document).ready(function() {
    var $section = $('.service_section');
    var sectionOffset = $section.offset().top; 
    var shown = false; 

    $(window).on('scroll', function() {
        var scrollTop = $(this).scrollTop(); 

        if (scrollTop + $(window).height() > sectionOffset && !shown) {
            shown = true; 
            $section.addClass('visible'); 
        } else if (scrollTop + $(window).height() <= sectionOffset && shown) {
            shown = false; 
            $section.removeClass('visible'); 
        }
    });
});

// carousel 
let currentCaption = 1;

function showCaption(number) {
    // Oculta todos los captions
    document.querySelectorAll('.caption').forEach(caption => {
        caption.style.display = 'none';
    });

    document.getElementById(`caption-${number}`).style.display = 'block';

    document.querySelectorAll('.nav-btn').forEach((btn, index) => {
        if (index === number - 1) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    currentCaption = number;
}

showCaption(1);
