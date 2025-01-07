import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

# Función para obtener la portada y el link de compra desde Giglon
def obtener_info_giglon(url_giglon):
    print(f"Accediendo a Giglon en {url_giglon}")
    
    try:
        response = requests.get(url_giglon)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraer la portada desde el meta tag "og:image"
            portada_tag = soup.find('meta', property='og:image')
            if portada_tag and 'content' in portada_tag.attrs:
                portada = portada_tag['content']
            else:
                print("No se encontró la portada. Revisando HTML...")
                portada = '/static/images/sincaratula.jpg'
            print(f"Portada encontrada: {portada}")

            # Extraer el enlace de compra
            comprar_button = soup.find('button', {'id': 'comprarButton'})
            if comprar_button and 'onclick' in comprar_button.attrs:
                link_compra = comprar_button['onclick'].split('"')[1]
            else:
                # Si no se encuentra el botón, intentamos con el enlace directamente
                comprar_button = soup.find('a', class_='fasc-button')
                if comprar_button and 'href' in comprar_button.attrs:
                    link_compra = comprar_button['href']
                else:
                    link_compra = None  # Cambiado a None para filtrar después
            print(f"Link de compra encontrado: {link_compra}")

            return portada, link_compra
        else:
            print(f"Error al acceder a Giglon: {response.status_code}")
            return '/static/images/sincaratula.jpg', None
    except Exception as e:
        print(f"Error durante la extracción en Giglon: {str(e)}")
        return '/static/images/sincaratula.jpg', None


# Función para obtener el enlace correcto de Giglon desde la página intermedia
def obtener_enlace_giglon(url_pelicula):
    print(f"Accediendo a la página intermedia en {url_pelicula}")
    
    try:
        response = requests.get(url_pelicula)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraer el enlace correcto a Giglon, filtrando solo el botón que contiene "idEvent" en el enlace
            botones_compra = soup.find_all('a', class_='fasc-button')
            for boton in botones_compra:
                if 'idEvent' in boton['href']:
                    enlace_giglon = boton['href']
                    print(f"Enlace a Giglon encontrado: {enlace_giglon}")
                    return enlace_giglon
            print("No se encontró el enlace correcto a Giglon.")
            return None
        else:
            print(f"Error al acceder a la página intermedia: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error durante la extracción de enlace a Giglon: {str(e)}")
        return None


# Función principal para scrapear la página de Artistic Metropol
def scrape_artistic_metropol():
    # Obtener la fecha actual y formatearla en el formato requerido
    fecha_actual = datetime.now().strftime('%Y-%m-%d')

    # Construir la URL con la fecha actual
    base_url = 'https://artisticmetropol.es/'
    URL = f'{base_url}calendario-de-sesiones/{fecha_actual}/'

    print(f"Accediendo a la página principal: {URL}")

    response = requests.get(URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen películas
        peliculas = soup.find_all('div', class_='tribe-events-calendar-day__event-content')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Extraer el título y el enlace
                titulo_tag = pelicula.find('a', class_='tribe-events-calendar-day__event-title-link')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'
                enlace_pelicula = titulo_tag['href'] if titulo_tag and 'href' in titulo_tag.attrs else 'Enlace no disponible'

                # Excluir películas con "Pase PRIVADO"
                if 'Pase PRIVADO' in titulo:
                    continue

                # Eliminar la sala del título usando expresión regular
                titulo = re.sub(r'^SALA \d+:\s*', '', titulo)

                # Extraer la hora de la sesión
                hora_tag = pelicula.find('span', class_='tribe-event-date-start')
                hora = hora_tag.text.split('|')[-1].strip() if hora_tag else 'Hora no disponible'

                # Obtener el enlace a Giglon desde la página intermedia
                enlace_giglon = obtener_enlace_giglon(enlace_pelicula)

                # Si se encuentra el enlace de Giglon, obtener la información adicional
                if enlace_giglon:
                    portada, link_compra = obtener_info_giglon(enlace_giglon)

                    # Sólo añadir películas que tienen un "Link de compra" disponible
                    if link_compra:
                        # Crear la estructura de datos solicitada
                        row = {
                            'Carátula': portada,
                            'Título': titulo,
                            'Director': 'Director no disponible',  # Director no disponible
                            'Duración': 'Duración no disponible',  # Duración no disponible
                            'Versión': 'Versión no disponible'     # Versión no disponible
                        }

                        # Información de la sesión 1
                        sesiones_info = [{'hora': hora, 'enlace': link_compra}]

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

            # Imprimir el DataFrame para verificar los datos
            print(df)

            return df
        else:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()
    else:
        print(f"Error al acceder a la página principal: {response.status_code}")
        return pd.DataFrame()

# Ejecutar la función
scrape_artistic_metropol()
