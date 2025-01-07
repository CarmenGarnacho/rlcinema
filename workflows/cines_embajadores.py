import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_cines_embajadores():
    # Obtener la fecha actual en el formato "dd/mm"
    hoy = datetime.now().strftime('%d/%m')

    # URL de la página de cine que vas a scrapear
    URL = 'https://cinesembajadores.es/madrid/'
    response = requests.get(URL)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen películas
        peliculas = soup.find_all('li', class_='movie')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Extraer el título
                titulo_tag = pelicula.find('h2').find('a')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer la duración
                duracion_tag = pelicula.find('li', class_='minutos')
                duracion = duracion_tag.text.strip() if duracion_tag else 'Duración no disponible'

                # Extraer la versión (VOS, VOSE, etc.)
                version_tag = pelicula.find('li', class_='doblaje')
                version = version_tag.text.strip() if version_tag else 'Versión no disponible'

                # Extraer el director
                more_info = pelicula.find('div', class_='more')
                if more_info:
                    director_tag = more_info.find('h5')
                    if director_tag and 'Director' in director_tag.text:
                        director_text = director_tag.text
                        director = director_text.split(':', 1)[1].strip() if ':' in director_text else 'Director no disponible'
                    else:
                        director = 'Director no disponible'
                else:
                    director = 'Director no disponible'

                # Extraer la carátula (imagen) de la película
                imagen_tag = pelicula.find('div', class_='poster').find('img')
                imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                # Extraer las sesiones del día de hoy
                sesiones_div = pelicula.find('div', class_='tabla-horarios')
                sesiones_info = []
                if sesiones_div:
                    sesiones = sesiones_div.find_all('p', {'data-hora': True})
                    for sesion in sesiones:
                        # Filtrar por el día de hoy
                        dia_sesion = sesion['data-dia'] if 'data-dia' in sesion.attrs else ''
                        if dia_sesion == hoy:
                            sala = sesion['data-sala'] if 'data-sala' in sesion.attrs else 'Sala no disponible'
                            hora = sesion['data-hora'] if 'data-hora' in sesion.attrs else 'Hora no disponible'
                            enlace_compra = sesion.find('a')['href'] if sesion.find('a') else 'Enlace no disponible'
                            sesiones_info.append({
                                'sala': sala,
                                'hora': hora,
                                'enlace': enlace_compra
                            })

                # Solo incluir la película si hay sesiones del día de hoy
                if sesiones_info:
                    # Crear una fila para el DataFrame
                    row = {
                        'Carátula': imagen,
                        'Título': titulo,
                        'Director': director,
                        'Duración': duracion,
                        'Versión': version
                    }

                    # Añadir sesiones a la fila
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

            # Imprimir el DataFrame
            print(df)
            return df
        else:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_cines_embajadores()
