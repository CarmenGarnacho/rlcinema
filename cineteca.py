import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from babel.dates import format_date

# Usar babel para obtener el nombre del mes en español
def get_month_name():
    """Obtiene el nombre del mes actual en español usando babel."""
    return format_date(datetime.today(), format='MMMM', locale='es').capitalize()

def get_today_date():
    """Obtiene la fecha de hoy en formato YYYY-MM-DD."""
    today = datetime.today()
    return today.strftime('%Y-%m-%d')

def scrape_cineteca_programacion():
    # Obtener la fecha de hoy y el mes actual
    today = get_today_date()
    mes_actual = get_month_name()

    # URL dinámica con la fecha de hoy
    base_url = "https://www.cinetecamadrid.com/programacion?s=&to={}&since={}"
    url = base_url.format(today, today)
    response = requests.get(url)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen películas
        peliculas = soup.find_all('div', class_='node node--type-activity node--view-mode-teaser ds-1col clearfix')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Extraer el título
                titulo_tag = pelicula.find('h2', class_='title').find('a')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer la carátula (imagen) de la película
                imagen_tag = pelicula.find('div', class_='image-holder').find('img')
                imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'
                imagen = "https://www.cinetecamadrid.com" + imagen if imagen != 'Imagen no disponible' else imagen

                # Versión (no disponible en esta página, se dejará fijo)
                version = 'Versión no disponible'

                # Obtener el enlace de la sesión
                enlace_sesion_url = "https://www.cinetecamadrid.com" + titulo_tag['href']

                # Scraping de la página de la sesión para extraer el link de compra y el director
                response_sesion = requests.get(enlace_sesion_url)
                if response_sesion.status_code == 200:
                    sesion_soup = BeautifulSoup(response_sesion.content, 'html.parser')
                    # Extraer el enlace de compra usando 'string' en lugar de 'text'
                    enlace_compra_tag = sesion_soup.find('a', href=True, string="Comprar entradas")
                    enlace_compra = enlace_compra_tag['href'] if enlace_compra_tag else 'Link no disponible'

                    # Extraer el director
                    director_tag = sesion_soup.find('div', class_='field field--name-field-director field--type-string field--label-hidden field__item')
                    director = director_tag.text.strip() if director_tag else 'Director no disponible'
                else:
                    enlace_compra = 'Link no disponible'
                    director = 'Director no disponible'

                # Extraer la duración y quitar paréntesis
                duracion_tag = pelicula.find('div', class_='field field-name-field-duration')
                duracion = duracion_tag.find('span').text.strip().replace("'", ' minutos') if duracion_tag else 'Duración no disponible'
                duracion = duracion.replace('(', '').replace(')', '')  # Quitar paréntesis

                # Extraer las sesiones
                sesiones_tag = pelicula.find('div', class_='field--name-field-dias-de-proyeccion')
                sesiones_info = []
                if sesiones_tag:
                    sesiones_raw = sesiones_tag.find_all('div')
                    for sesion_raw in sesiones_raw:
                        sesion_text = sesion_raw.text.strip()
                        # Reemplazar el nombre del mes dinámicamente
                        if mes_actual in sesion_text and "(" in sesion_text:
                            try:
                                dia, hora = sesion_text.split("(")
                                dia = dia.replace(f'{mes_actual}:', '').strip()
                                hora = hora.replace(')', '').strip()

                                sesiones_info.append({
                                    'dia': dia,
                                    'hora': hora,
                                    'enlace': enlace_compra
                                })
                            except ValueError:
                                print(f"Error procesando la sesión: {sesion_text}")
                        else:
                            print(f"Formato de sesión no esperado: {sesion_text}")

                # Crear una fila para el DataFrame con la estructura solicitada
                row = {
                    'Carátula': imagen,
                    'Título': titulo,
                    'Director': director,  # Director extraído desde la página de la sesión
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

# Ejemplo de ejecución
if __name__ == "__main__":
    scrape_cineteca_programacion()
