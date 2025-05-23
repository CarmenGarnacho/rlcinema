function cargarTabla(url, tablaId, procesarFila) {
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Error al cargar ${url}`);
            return response.json();
        })
        .then(data => {
            const tabla = document.querySelector(`#${tablaId} tbody`);
            tabla.innerHTML = ''; // Limpia la tabla antes de cargar los datos
            data.forEach(item => {
                const fila = procesarFila(item);
                tabla.insertAdjacentHTML('beforeend', fila);
            });
        })
        .catch(error => console.error('Error:', error));
}

function generarBotonesSesiones(item) {
    let botones = '';
    for (let i = 1; i <= 6; i++) {
        if (item[`Sesión ${i}`]) {
            botones += `<a href="${item[`Link Sesión ${i}`]}" class="session-button" target="_blank">${item[`Sesión ${i}`]}</a>`;
        }
    }
    return botones || 'N/A';
}

function filaCartelera(item) {
    return `
        <tr>
            <td>${item.Cine || 'N/A'}</td>
            <td><img src="${item['Carátula']}" alt="Carátula" style="width: 80px;"></td>
            <td>${item.Título || 'Sin título'}</td>
            <td>${item.Director || 'Desconocido'}</td>
            <td>${item.Duración || 'No disponible'}</td>
            <td>${item.Versión || 'N/A'}</td>
            <td>${generarBotonesSesiones(item)}</td>
        </tr>
    `;
}

function filaTeatro(item) {
    return `
        <tr>
            <td>${item.Teatro || 'N/A'}</td>
            <td><img src="${item['Carátula']}" alt="Carátula" style="width: 80px;"></td>
            <td>${item.Título || 'Sin título'}</td>
            <td>${item.Director || 'Desconocido'}</td>
            <td>${item.Duración || 'No disponible'}</td>
            <td>${item.Versión || 'N/A'}</td>
            <td>${item.Sesión_1 || 'Sin sesiones'}</td>
        </tr>
    `;
}

function filaExposiciones(item) {
    return `
        <tr>
            <td><img src="${item['Carátula Exposición']}" alt="Carátula" style="width: 80px;"></td>
            <td>${item.Exposición || 'N/A'}</td>
            <td>${item.Descripción || 'Sin descripción'}</td>
            <td>${item.Lugar || 'Lugar no disponible'}</td>
            <td>${item.Fechas || 'No disponible'}</td>
            <td>${item.Precio || 'Gratis'}</td>
            <td><a href="${item.Entradas || '#'}" target="_blank">Entradas</a></td>
        </tr>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.nav-link');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();

            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(pane => pane.classList.remove('active', 'show'));

            tab.classList.add('active');
            const targetPane = document.querySelector(tab.getAttribute('href'));
            if (targetPane) {
                targetPane.classList.add('active', 'show');
            }

            if (tab.id === 'tab-cine') {
                cargarTabla('./data/cartelera.json', 'tabla-cine', filaCartelera);
            } else if (tab.id === 'tab-teatro') {
                cargarTabla('./data/cartelerateatro.json', 'tabla-teatro', filaTeatro);
            } else if (tab.id === 'tab-exposiciones') {
                cargarTabla('./data/exposiciones.json', 'tabla-exposiciones', filaExposiciones);
            }
        });
    });

    cargarTabla('./data/cartelera.json', 'tabla-cine', filaCartelera);
});

function convertMinutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

document.addEventListener("DOMContentLoaded", () => {
    $("#slider-range").slider({
        range: true,
        min: 0,
        max: 1440,
        step: 15,
        values: [600, 1320],
        slide: function(event, ui) {
            const startTime = convertMinutesToTime(ui.values[0]);
            const endTime = convertMinutesToTime(ui.values[1]);
            $("#label-inicio").text(startTime);
            $("#label-fin").text(endTime);
            filtrarSesiones(startTime, endTime);
        }
    });

    const initialStart = convertMinutesToTime($("#slider-range").slider("values", 0));
    const initialEnd = convertMinutesToTime($("#slider-range").slider("values", 1));

    $("#label-inicio").text(initialStart);
    $("#label-fin").text(initialEnd);
});

function filtrarSesiones(horaInicio, horaFin) {
    const filas = document.querySelectorAll("#tabla-cine tbody tr");
    filas.forEach(fila => {
        let mostrar = false;
        fila.querySelectorAll(".session-button").forEach(boton => {
            const hora = boton.textContent.trim();
            if (hora >= horaInicio && hora <= horaFin) {
                mostrar = true;
            }
        });
        fila.style.display = mostrar ? "" : "none";
    });
}
