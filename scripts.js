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

function filtrarSesiones(horaInicio, horaFin) {
    const tablas = document.querySelectorAll('table[id^="tabla-"]');

    tablas.forEach(tabla => {
        const filas = tabla.querySelectorAll('tbody tr');

        filas.forEach(fila => {
            const botones = fila.querySelectorAll('.session-button');
            let mostrarFila = false;

            botones.forEach(boton => {
                const horaSesion = boton.textContent.trim();
                if (horaSesion && compararHoras(horaSesion, horaInicio, horaFin)) {
                    mostrarFila = true;
                    boton.style.display = 'inline-block';
                } else {
                    boton.style.display = 'none';
                }
            });

            fila.style.display = mostrarFila ? 'table-row' : 'none';
        });
    });
}

function compararHoras(horaSesion, horaInicio, horaFin) {
    const [horaS, minutoS] = horaSesion.split(':').map(Number);
    const [horaI, minutoI] = horaInicio.split(':').map(Number);
    const [horaF, minutoF] = horaFin.split(':').map(Number);

    const minutosSesion = horaS * 60 + minutoS;
    const minutosInicio = horaI * 60 + minutoI;
    const minutosFin = horaF * 60 + minutoF;

    return minutosSesion >= minutosInicio && minutosSesion <= minutosFin;
}

document.addEventListener('DOMContentLoaded', () => {
    const rango = document.querySelector('.rangoTiempo');
    const slider = document.getElementById('slider-range');

    slider.addEventListener('input', () => {
        const horaInicio = '15:00'; // Obtener valor del slider
        const horaFin = '23:59'; // Obtener valor del slider

        rango.textContent = `${horaInicio} - ${horaFin}`;
        filtrarSesiones(horaInicio, horaFin);
    });
});
