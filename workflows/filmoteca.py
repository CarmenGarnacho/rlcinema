import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_filmoteca():
    # Obtener la fecha actual y formatearla en el formato requerido
    fecha_actual = datetime.now().strftime('%d/%m/%Y 0:00:00')
    
    # Construir la URL con la fecha actual
    base_url = 'https://entradasfilmoteca.gob.es/'
    URL = f'{base_url}Busqueda.aspx?fecha={fecha_actual}'
    
    response = requests.get(URL)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen películas
        peliculas = soup.find_all('div', class_='thumbnail thumPelicula')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Extraer la carátula (imagen) de la película
                imagen_tag = pelicula.find('input', type='image')
                imagen = base_url + imagen_tag['src'] if imagen_tag and 'src' in imagen_tag.attrs else 'Imagen no disponible'

                # Extraer el título (que es el enlace con la clase 'linkPelicula')
                titulo_tag = pelicula.find('a', class_='linkPelicula')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer el director o la temática (que es el texto en el <h3>)
                director_tag = pelicula.find('h3')
                director = director_tag.text.strip() if director_tag else 'Director no disponible'

                # Extraer la sesión
                session_tag = pelicula.find('h2')
                session_text = session_tag.text.strip() if session_tag else 'Sesión no disponible'
                
                # Corregir para extraer solo la hora
                if '·' in session_text:
                    fecha_hora, sala = session_text.split('·', 1)
                    # Extraer solo la hora eliminando la fecha (suponiendo que la hora siempre estará después de la fecha)
                    hora = fecha_hora.split()[-1].strip()  # Esto toma el último elemento (la hora)
                else:
                    hora, sala = 'Hora no disponible', 'Sala no disponible'

                # Extraer el enlace de compra
                enlace_compra_tag = pelicula.find('a', class_='btn btn-primary')
                enlace_compra = base_url + enlace_compra_tag['href'] if enlace_compra_tag and 'href' in enlace_compra_tag.attrs else 'Enlace no disponible'

                # Para este caso, vamos a suponer que cada película tiene una única sesión
                sesiones_info = [{'hora': hora, 'enlace': enlace_compra}]

                # Crear una fila para el DataFrame
                row = {
                    'Carátula': imagen,
                    'Título': titulo,
                    'Director': director,
                    'Duración': 'Duración no disponible',
                    'Versión': 'Versión no disponible'
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
