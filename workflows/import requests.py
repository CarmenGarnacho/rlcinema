import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_sala_equis():
    # URL de la página de cine que vamos a scrapear
    URL = 'https://salaequis.es/taquilla/'
    response = requests.get(URL)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer todas las secciones de películas
        peliculas = soup.find_all('div', class_='row')

        data = []
        if peliculas:
            for pelicula in peliculas:
                # Extraer el título y el enlace a los detalles
                titulo_tag = pelicula.find('div', class_='title bigFont').find('a')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'
                link_detalle = titulo_tag['href'] if titulo_tag else None
                
                # Extraer la carátula
                caratula_tag = pelicula.find('div', class_='image').find('img')
                caratula = caratula_tag['src'] if caratula_tag else 'Carátula no disponible'

                # Si hay un link a los detalles, procedemos a extraer la información adicional
                if link_detalle:
                    director, duracion, version = scrape_detalle_pelicula(link_detalle)

                # Extraer el enlace de compra de entradas (el link a Kinetike)
                enlace_compra_tag = pelicula.find('div', class_='buy bigFont').find('a')
                enlace_compra = enlace_compra_tag['href'] if enlace_compra_tag else 'Enlace no disponible'

                # Extraer las sesiones de la película
                sesiones_info = scrape_sesiones_kinetike(enlace_compra)

                # Crear una fila con los datos de la película
                row = {
                    'Carátula': caratula,
                    'Título': titulo,
                    'Director': director,
                    'Duración': duracion,
                    'Versión': version
                }

                # Añadir sesiones a la fila (solo mostramos la sesión de hoy)
                for i, sesion in enumerate(sesiones_info, start=1):
                    row[f'Sesión {i}'] = sesion['hora']
                    row[f'Link Sesión {i}'] = sesion['enlace']
                
                # Rellenar el resto de las columnas de sesión si hay menos de 5
                max_sesiones = len(sesiones_info)
                for i in range(max_sesiones + 1, 6):
                    row[f'Sesión {i}'] = None
                    row[f'Link Sesión {i}'] = None

                data.append(row)

            # Crear un DataFrame con los datos
            df = pd.DataFrame(data)
            return df
        else:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

def scrape_detalle_pelicula(link_detalle):
    """
    Función para extraer el director, la duración y la versión de la película desde la página de detalles.
    """
    response = requests.get(link_detalle)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Buscar la información en la sección de shortDescription
        info_tag = soup.find('div', class_='shortDescription')
        if info_tag:
            texto_info = info_tag.text.strip().split('\n')
            director = texto_info[1].split('/')[0].strip() if len(texto_info) > 1 else 'Director no disponible'
            duracion = texto_info[-1].split(' ')[0] + ' min' if 'min' in texto_info[-1] else 'Duración no disponible'
            version = texto_info[-2].split('–')[1].strip() if '–' in texto_info[-2] else 'Versión no disponible'
        else:
            director = 'Director no disponible'
            duracion = 'Duración no disponible'
            version = 'Versión no disponible'
        
        return director, duracion, version
    else:
        return 'Director no disponible', 'Duración no disponible', 'Versión no disponible'

def scrape_sesiones_kinetike(link_kinetike):
    """
    Función para extraer las sesiones de la película en Kinetike.
    Solo extraemos las sesiones del día actual.
    """
    response = requests.get(link_kinetike)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Fecha actual
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        # Extraer las sesiones
        sesiones = soup.find_all('div', class_='row no-gutters shadow-lg border rounded')
        sesiones_info = []
        for sesion in sesiones:
            dia_tag = sesion.find('span', style="font-size:medium")
            fecha_sesion = dia_tag.text.strip() if dia_tag else None

            # Filtrar por la fecha de hoy
            if fecha_sesion == fecha_hoy:
                # Extraer la hora de la sesión
                hora_tag = sesion.find('input', class_='btn btn-info')
                hora = hora_tag['value'] if hora_tag else 'Hora no disponible'
                enlace = link_kinetike  # Link a la sesión (usamos el link principal de Kinetike)
                sesiones_info.append({'hora': hora, 'enlace': enlace})

        return sesiones_info
    else:
        return []

# Si quieres probar el script directamente
if __name__ == "__main__":
    df = scrape_sala_equis()
    # Mostrar el DataFrame resultante
    print(df)
