document.addEventListener("DOMContentLoaded", function() {
    let currentLanguage = "es";
    
    // Element that will change its content
    const sloganElement = document.getElementById("slogan");
    const titleElement = document.getElementById("title");
    const downloadElement = document.getElementById("download");
    const textdownloadElement = document.getElementById("text-download");
    const esElement = document.getElementById("es");
    const enElement = document.getElementById("en");
    const ptElement = document.getElementById("pt");
    const languageElement  = document.getElementById("languageDropdown");
    const navElement  = document.getElementById("nav");
    
    
    const usElement = document.getElementById("us");
    const identityElement = document.getElementById("identity");
    const missionElement = document.getElementById("mission");
    const visionElement = document.getElementById("vision");
    const valorElement = document.getElementById("valor");

    const pOneElement = document.getElementById("p-one");
    const pTwoElement = document.getElementById("p-two");
    const pThreeElement = document.getElementById("p-three");

    const fraternityElement = document.getElementById("fraternity");
    const transparencyElement = document.getElementById("transparency");
    const impartialityElement = document.getElementById("impartiality");
    const sustainabilityElement = document.getElementById("sustainability");
    const collectiveConstructionElement = document.getElementById("collectiveConstruction");
    const servicesTitleElement = document.getElementById("services-title");
    const workshopTitleElement = document.getElementById("workshop-title");
    const workshopDescriptionElement = document.getElementById("workshop-description");
    const entrepreneurshipTitleElement = document.getElementById("entrepreneurship-title");
    const entrepreneurshipDescriptionElement = document.getElementById("entrepreneurship-description");
    const volunteeringTitleElement = document.getElementById("volunteering-title");
    const volunteeringDescriptionElement = document.getElementById("volunteering-description");
    const galleryTitleElement = document.getElementById("gallery-title");
    const teamTitleElement = document.getElementById("title-team");
    const roleAndreaElement = document.getElementById("role-andrea");
    const roleMariaElement = document.getElementById("role-maria");
    const roleYormanElement = document.getElementById("role-yorman");
    const roleIzamarElement = document.getElementById("role-izamar");
    const roleEymarElement = document.getElementById("role-eymar");
    const addressInfoElement = document.getElementById("address-info");
    const locationInfoElement = document.getElementById("location-info");
    const footerText = document.getElementById("footer-text");

    // Function to change the content based on the language
    function changeLanguage(language) {
        switch (language) {
            case "es":
                sloganElement.textContent = "Somos una iniciativa de educomunicación que promueve el liderazgo de mujeres y jóvenes. Utilizamos herramientas prácticas para analizar y mejorar su entorno.";
                titleElement.textContent = "Asociación Civil EscuChamos";
                downloadElement.textContent = "¡Descarga nuestra App!";
                textdownloadElement.textContent = "Haz clic en el botón para descargar la aplicación de EscuChamos, donde encontrarás información importante y podrás interactuar con nuestra comunidad.";
                esElement.textContent = "Español";
                enElement.textContent = "Inglés";
                ptElement.textContent = "Portugués";
                languageElement.textContent = "Idioma";
                navElement.textContent = "Inicio";
                
                usElement.textContent = "Sobre Nosotros";
                identityElement.textContent = "IDENTIDAD";
                pOneElement.textContent = "Somos una iniciativa vinculada a la educomunicación desde la perspectiva de la comunicación para el desarrollo, que busca promover entre las comunidades el liderazgo de mujeres y jóvenes, valiéndose de mecanismos para el análisis de su realidad y herramientas prácticas para configurar mejoras de su entorno desde los ciudadanos en especial en niños, niñas, adolescentes, jóvenes y mujeres.";
                missionElement.textContent = "MISIÓN";
                pTwoElement.textContent = "Buscamos alcanzar la promoción social con acciones que mejoren las capacidades individuales y colectivas en las comunidades desde la educación y las herramientas comunicacionales para el fortalecimiento de la identidad comunitaria, la vivencia de herramientas de resolución de conflictos y el emprendimiento para la reconstrucción del tejido social.";
                
                visionElement.textContent = "VISIÓN";
                pThreeElement.textContent = "Constituirnos en una red de ciudadanos proactivos conectados en diversos puntos del país y del mundo desde la educomunicación con poder de convocatoria y movilización en las comunidades para gestionar intervención de los contextos desde los ciudadanos y su incidencia local, para alcanzar mejoras sostenibles de sus proyectos de vida individuales y colectivos.";
                valorElement.textContent = "VALORES DE LA RED";
                fraternityElement.textContent = "• Fraternidad";
                transparencyElement.textContent = "• Transparencia";
                impartialityElement.textContent = "• Imparcialidad";
                sustainabilityElement.textContent = "• Sostenibilidad";
                collectiveConstructionElement.textContent = "• Construcción colectiva";
                servicesTitleElement.innerHTML = "Nuestros <span>Servicios</span>";
                workshopTitleElement.textContent = "Talleres de Educomunicación y Liderazgo Comunitario";
                workshopDescriptionElement.textContent = "Ofrecer talleres y capacitaciones para mujeres, jóvenes, y adolescentes en temas de educomunicación, liderazgo, resolución de conflictos y fortalecimiento de la identidad comunitaria. Estos talleres permitirían a los participantes desarrollar habilidades prácticas para analizar su realidad, identificar problemas y diseñar soluciones desde una perspectiva de comunicación para el desarrollo.";
                entrepreneurshipTitleElement.textContent = "Programas de Emprendimiento Social";
                entrepreneurshipDescriptionElement.textContent = "Implementar programas que fomenten el emprendimiento entre los ciudadanos, especialmente enfocados en mujeres y jóvenes. Estos programas podrían incluir formación en habilidades empresariales, acceso a recursos y asesoramiento para la creación de proyectos que contribuyan a la reconstrucción del tejido social y al desarrollo sostenible de las comunidades.";
                volunteeringTitleElement.textContent = "Red de Voluntariado y Movilización Comunitaria";
                volunteeringDescriptionElement.textContent = "Crear y gestionar una red de voluntarios comprometidos con la promoción social y la mejora de las capacidades comunitarias. Esta red podría llevar a cabo actividades de movilización para intervenir en contextos locales, impulsar proyectos comunitarios y promover la participación activa de los ciudadanos en la mejora de su entorno, tanto a nivel local como global.";
                
                galleryTitleElement.innerHTML = "Nuestra <span>Galería</span>";
                teamTitleElement.innerHTML = "Nuestro <span>Equipo</span>";
                roleAndreaElement.textContent = "Directora";
                roleMariaElement.textContent = "Coordinadora de proyectos";
                roleYormanElement.textContent = "Coordinador de comunicaciones";
                roleIzamarElement.textContent = "Coordinadora de promoción social";
                roleEymarElement.textContent = "Coordinador jurídico";
                addressInfoElement.innerHTML = "<strong>Asociación Civil EscuChamos</strong><br>San Martín, detrás del Estadio Leonardo Alarcón";
                locationInfoElement.innerHTML = "<br>Ubicada en San Martín, calle 10, detrás del Estadio Leonardo Alarcón, Rubio, Estado Táchira";
                footerText.innerHTML = '&copy; 2024 Todos los derechos reservados por <span class="brand-name">Escu</span><span class="brand-name2">Chamos</span>';
                currentLanguage = "es";

                break;


            case "en":
                sloganElement.textContent = "We are an educommunication initiative that promotes the leadership of women and young people. We use practical tools to analyze and improve their environment.";
                titleElement.textContent = "Civil Association EscuChamos";
                downloadElement.textContent = "Download our App!";
                textdownloadElement.textContent = "Click the button to download the EscuChamos app, where you will find important information and can interact with our community.";
                esElement.textContent = "Spanish";
                enElement.textContent = "English";
                ptElement.textContent = "Portuguese";
                languageElement.textContent = "Language";
                navElement.textContent = "Home";

                // Translation of additional elements
                usElement.textContent = "About Us";
                identityElement.textContent = "IDENTITY";
                pOneElement.textContent = "We are an initiative linked to educommunication from the perspective of communication for development, seeking to promote leadership among communities, especially of women and young people. We use mechanisms to analyze their reality and practical tools to improve their environment, especially for children, adolescents, young people, and women.";
                missionElement.textContent = "MISSION";
                pTwoElement.textContent = "We aim to achieve social promotion with actions that enhance individual and collective capacities in communities through education and communication tools to strengthen community identity, experience conflict resolution tools, and foster entrepreneurship to rebuild social ties.";
                visionElement.textContent = "VISION";
                pThreeElement.textContent = "To become a network of proactive citizens connected across different points of the country and the world through educommunication, with the power to call and mobilize communities to manage interventions in local contexts, achieving sustainable improvements in individual and collective life projects.";
                valorElement.textContent = "NETWORK VALUES";
                fraternityElement.textContent = "• Fraternity";
                transparencyElement.textContent = "• Transparency";
                impartialityElement.textContent = "• Impartiality";
                sustainabilityElement.textContent = "• Sustainability";
                collectiveConstructionElement.textContent = "• Collective Construction";
                
                servicesTitleElement.innerHTML = "Our <span>Services</span>";
                workshopTitleElement.textContent = "Educommunication and Community Leadership Workshops";
                workshopDescriptionElement.textContent = "Offering workshops and training for women, youth, and adolescents on educommunication, leadership, conflict resolution, and strengthening community identity. These workshops would enable participants to develop practical skills to analyze their reality, identify problems, and design solutions from a communication for development perspective.";
                entrepreneurshipTitleElement.textContent = "Social Entrepreneurship Programs";
                entrepreneurshipDescriptionElement.textContent = "Implementing programs that encourage entrepreneurship among citizens, especially focusing on women and youth. These programs could include training in business skills, access to resources, and guidance for creating projects that contribute to rebuilding the social fabric and sustainable community development.";
                volunteeringTitleElement.textContent = "Community Mobilization and Volunteering Network";
                volunteeringDescriptionElement.textContent = "Creating and managing a network of volunteers committed to social promotion and strengthening community capacities. This network could carry out mobilization activities to intervene in local contexts, promote community projects, and encourage active citizen participation in improving their environment, both locally and globally.";
                
                galleryTitleElement.innerHTML = "Our <span>Gallery</span>";
                teamTitleElement.innerHTML = "Our <span>Team</span>";
                roleAndreaElement.textContent = "Director";
                roleMariaElement.textContent = "Project Coordinator";
                roleYormanElement.textContent = "Communications Coordinator";
                roleIzamarElement.textContent = "Social Promotion Coordinator";
                roleEymarElement.textContent = "Legal Coordinator";
                addressInfoElement.innerHTML = "<strong>EscuChamos Civil Association</strong><br>San Martín, behind the Leonardo Alarcón Stadium";
                locationInfoElement.innerHTML = "<br>Located in San Martín, street 10, behind the Leonardo Alarcón Stadium, Rubio, Táchira State";
                footerText.innerHTML = '&copy; 2024 All rights reserved by <span class="brand-name">Escu</span><span class="brand-name2">Chamos</span>';

                currentLanguage = "en";
                break;


            case "pt":
                sloganElement.textContent = "Somos uma iniciativa de educomunicação que promove a liderança de mulheres e jovens. Utilizamos ferramentas práticas para analisar e melhorar seu entorno.";
                titleElement.textContent = "Associação Civil EscuChamos";
                downloadElement.textContent = "Baixe nosso App!";
                textdownloadElement.textContent = "Clique no botão para baixar o aplicativo EscuChamos, onde você encontrará informações importantes e poderá interagir com nossa comunidade.";
                esElement.textContent = "Espanhol";
                enElement.textContent = "Inglês";
                ptElement.textContent = "Português";
                languageElement.textContent = "linguagem";
                navElement.textContent = "Início";

                // Traduções dos elementos adicionais
                usElement.textContent = "Sobre Nós";
                identityElement.textContent = "IDENTIDADE";
                pOneElement.textContent = "Somos uma iniciativa vinculada à educomunicação sob a perspectiva da comunicação para o desenvolvimento, que busca promover nas comunidades a liderança de mulheres e jovens, utilizando mecanismos para análise de sua realidade e ferramentas práticas para configurar melhorias em seu ambiente, especialmente para crianças, adolescentes, jovens e mulheres.";
                missionElement.textContent = "MISSÃO";
                pTwoElement.textContent = "Buscamos alcançar a promoção social com ações que melhorem as capacidades individuais e coletivas nas comunidades por meio da educação e ferramentas de comunicação para o fortalecimento da identidade comunitária, experiência de ferramentas de resolução de conflitos e empreendedorismo para a reconstrução do tecido social.";
                visionElement.textContent = "VISÃO";
                pThreeElement.textContent = "Constituir-nos em uma rede de cidadãos proativos conectados em diversos pontos do país e do mundo por meio da educomunicação, com poder de convocação e mobilização nas comunidades para gerir intervenções nos contextos locais, alcançando melhorias sustentáveis em seus projetos de vida individuais e coletivos.";
                valorElement.textContent = "VALORES DA REDE";
                fraternityElement.textContent = "• Fraternidade";
                transparencyElement.textContent = "• Transparência";
                impartialityElement.textContent = "• Imparcialidade";
                sustainabilityElement.textContent = "• Sustentabilidade";
                collectiveConstructionElement.textContent = "• Construção coletiva";
                
                servicesTitleElement.innerHTML = "Nossos <span>Serviços</span>";
                workshopTitleElement.textContent = "Oficinas de Educomunicação e Liderança Comunitária";
                workshopDescriptionElement.textContent = "Oferecer oficinas e treinamentos para mulheres, jovens e adolescentes em temas de educomunicação, liderança, resolução de conflitos e fortalecimento da identidade comunitária. Estas oficinas permitiriam aos participantes desenvolver habilidades práticas para analisar sua realidade, identificar problemas e desenhar soluções a partir de uma perspectiva de comunicação para o desenvolvimento.";
                entrepreneurshipTitleElement.textContent = "Programas de Empreendedorismo Social";
                entrepreneurshipDescriptionElement.textContent = "Implementar programas que incentivem o empreendedorismo entre os cidadãos, especialmente focado em mulheres e jovens. Estes programas poderiam incluir formação em habilidades empresariais, acesso a recursos e orientação para criação de projetos que contribuam para reconstrução do tecido social e desenvolvimento sustentável das comunidades.";
                volunteeringTitleElement.textContent = "Rede de Voluntariado e Mobilização Comunitária";
                volunteeringDescriptionElement.textContent = "Criar e gerir uma rede de voluntários comprometidos com a promoção social e o fortalecimento das capacidades comunitárias. Esta rede poderia realizar atividades de mobilização para intervir em contextos locais, impulsionar projetos comunitários e promover a participação ativa dos cidadãos na melhoria de seu ambiente, tanto local quanto global.";
                
                galleryTitleElement.innerHTML = "Nossa <span>Galeria</span>";
                teamTitleElement.innerHTML = "Nossa <span>Equipe</span>"
                roleAndreaElement.textContent = "Diretora";
                roleMariaElement.textContent = "Coordenadora de projetos";
                roleYormanElement.textContent = "Coordenador de comunicações";
                roleIzamarElement.textContent = "Coordenadora de promoção social";
                roleEymarElement.textContent = "Coordenador jurídico";
                addressInfoElement.innerHTML = "<strong>Associação Civil EscuChamos</strong><br>San Martín, atrás do Estádio Leonardo Alarcón";
                locationInfoElement.innerHTML = "<br>Localizada em San Martín, rua 10, atrás do Estádio Leonardo Alarcón, Rubio, Estado Táchira";
                footerText.innerHTML = '&copy; 2024 Todos os direitos reservados por <span class="brand-name">Escu</span><span class="brand-name2">Chamos</span>';

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