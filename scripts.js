function cargarTabla(url, tablaId, procesarFila) {
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Error al cargar ${url}`);
            return response.json();
        })
        .then(data => {
            const tabla = document.querySelector(`#${tablaId} tbody`);
            tabla.innerHTML = ''; // Limpia el contenido previo
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
            <td>${generarBotonesSesiones(item)}</td>
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
            panes.forEach(pane => pane.classList.remove('active'));

            tab.classList.add('active');
            const targetPane = document.querySelector(tab.getAttribute('href'));
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // Carga de datos
    cargarTabla('./data/cartelera.json', 'tabla-cine', filaCartelera);
    cargarTabla('./data/cartelerateatro.json', 'tabla-teatro', filaTeatro);
    cargarTabla('./data/exposiciones.json', 'tabla-exposiciones', filaExposiciones);
});

document.addEventListener('DOMContentLoaded', () => {
    const sliderInicio = document.getElementById('slider-inicio');
    const sliderFin = document.getElementById('slider-fin');
    const labelInicio = document.getElementById('label-inicio');
    const labelFin = document.getElementById('label-fin');

    // Actualiza las etiquetas y realiza el filtrado
    function actualizarEtiquetasYFiltrar() {
        const horaInicio = convertirMinutosAHoras(sliderInicio.value);
        const horaFin = convertirMinutosAHoras(sliderFin.value);

        labelInicio.textContent = horaInicio;
        labelFin.textContent = horaFin;

        filtrarSesiones(horaInicio, horaFin);
    }

    // Convierte minutos en formato HH:MM
    function convertirMinutosAHoras(minutos) {
        const horas = Math.floor(minutos / 60);
        const mins = minutos % 60;
        return `${horas.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }

    // Control de eventos
    sliderInicio.addEventListener('input', () => {
        if (parseInt(sliderInicio.value) >= parseInt(sliderFin.value)) {
            sliderInicio.value = sliderFin.value - 15; // Evita cruce de rangos
        }
        actualizarEtiquetasYFiltrar();
    });

    sliderFin.addEventListener('input', () => {
        if (parseInt(sliderFin.value) <= parseInt(sliderInicio.value)) {
            sliderFin.value = parseInt(sliderInicio.value) + 15; // Evita cruce de rangos
        }
        actualizarEtiquetasYFiltrar();
    });

    // Inicialización
    actualizarEtiquetasYFiltrar();
});

