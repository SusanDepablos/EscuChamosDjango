document.addEventListener("DOMContentLoaded", function() {
    let currentLanguage = "es";
    
    // Element that will change its content
    const sloganElement = document.getElementById("slogan");

    // Function to change the content based on the language
    function changeLanguage(language) {
        switch (language) {
            case "es":
                sloganElement.textContent = "Somos una iniciativa de educomunicación que promueve el liderazgo de mujeres y jóvenes. Utilizamos herramientas prácticas para analizar y mejorar su entorno.";
                currentLanguage = "es";
                break;
            case "en":
                sloganElement.textContent = "We are an educommunication initiative that promotes the leadership of women and young people. We use practical tools to analyze and improve their environment.";
                currentLanguage = "en";
                break;
            case "pt":
                sloganElement.textContent = "Somos uma iniciativa de educomunicação que promove a liderança de mulheres e jovens. Utilizamos ferramentas práticas para analisar e melhorar seu ambiente.";
                currentLanguage = "pt";
                break;
        }
    }

    // Listen for clicks on the language links
    const languageLinks = document.querySelectorAll(".dropdown-item");
    languageLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            const selectedLanguage = this.getAttribute("data-lang");
            changeLanguage(selectedLanguage);
        });
    });

    // Initialize with the current language
    changeLanguage(currentLanguage);
});