import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from babel.dates import format_date
from urllib.parse import urljoin

# Función para formatear la fecha de hoy
def get_today_formatted():
    """Obtiene la fecha de hoy en el formato usado por la página: Ej. 'Mié, 18 Sep'."""
    return format_date(datetime.today(), format="EEE, d MMM", locale='es').replace('sept', 'Sep')

# Función principal para hacer scraping de la página
def scrape_circulo_bellas_artes():
    # URL de la página principal
    base_url = "https://www.circulobellasartes.com"
    url = urljoin(base_url, "cine-estudio/")
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Obtener la fecha de hoy formateada
        today = get_today_formatted().strip().lower()
        print(f"Hoy es: {today}")

        peliculas_hoy = soup.find_all('div', class_='cba_cine_table_container')
        data = []
        sesiones_info_global = {}

        # Procesar cada entrada de película para hoy
        for pelicula in peliculas_hoy:
            dia = pelicula.find('div', class_='cba_cine_table_dia').text.strip().lower()

            if today == dia:
                sesiones_container = pelicula.find('div', class_='cba_cine_sesiones_container')
                horas = sesiones_container.find_all('div', class_='cba_cine_table_hora')
                titulos = sesiones_container.find_all('div', class_='cba_cine_table_titulo')

                for i in range(len(horas)):
                    hora = horas[i].text.strip()
                    titulo_tag = titulos[i].find('a')
                    titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                    enlace_pelicula = urljoin(base_url, titulo_tag['href'])

                    # Hacer la solicitud a la página de detalles de la película
                    response_pelicula = requests.get(enlace_pelicula)
                    if response_pelicula.status_code == 200:
                        pelicula_soup = BeautifulSoup(response_pelicula.content, 'html.parser')

                        # Paso 1: Extraer la carátula (imagen del póster)
                        img_tag = pelicula_soup.find('img', src=lambda src: src and 'uploads/2024/' in src or 'uploads/2025/' in src)
                        if img_tag:
                            imagen = img_tag.get('src', 'Imagen no disponible')
                            imagen = urljoin(base_url, imagen)
                        else:
                            imagen = 'Imagen no disponible'

                        # Paso 2: Extraer el director
                        director_tag = pelicula_soup.find('td', string='Dirección')
                        director = director_tag.find_next_sibling('td').text.strip() if director_tag else 'Director no disponible'

                        # Paso 3: Extraer la versión y la duración
                        version_tag = pelicula_soup.find('td', string='Versión')
                        version = version_tag.find_next_sibling('td').text.strip() if version_tag else 'Versión no disponible'
                        duracion_tag = pelicula_soup.find('td', string='Duración')
                        duracion = duracion_tag.find_next_sibling('td').text.strip() if duracion_tag else 'Duración no disponible'

                        # Paso 4: Extraer el enlace de compra de entradas
                        enlace_compra_tag = pelicula_soup.find('a', href=lambda href: href and href.startswith('https://www.reservaentradas.com/sesiones/madrid/circulobellasartes'))
                        if enlace_compra_tag:
                            enlace_compra = urljoin(base_url, enlace_compra_tag['href'])
                        else:
                            enlace_compra = 'Link no disponible'

                        # Si el título ya existe, añadir la sesión adicional
                        if titulo in sesiones_info_global:
                            sesiones_info_global[titulo]['sesiones'].append({'hora': hora, 'enlace': enlace_compra})
                        else:
                            # Si el título no existe, añadirlo con la sesión
                            sesiones_info_global[titulo] = {
                                'Carátula': imagen,
                                'Título': titulo,
                                'Director': director,
                                'Duración': duracion,
                                'Versión': version,
                                'sesiones': [{'hora': hora, 'enlace': enlace_compra}]
                            }

        # Ahora, organizar las sesiones en el DataFrame
        for titulo, movie_data in sesiones_info_global.items():
            row = {
                'Carátula': movie_data['Carátula'],
                'Título': movie_data['Título'],
                'Director': movie_data['Director'],
                'Duración': movie_data['Duración'],
                'Versión': movie_data['Versión']
            }

            # Añadir sesiones a la fila
            session_index = 0
            for j, sesion in enumerate(movie_data['sesiones'], start=1):
                row[f'Sesión {j}'] = sesion['hora']
                row[f'Link Sesión {j}'] = sesion['enlace']
                session_index += 1

            # Rellenar las columnas de sesión restantes si hay menos de 5
            for j in range(session_index + 1, 6):
                row[f'Sesión {j}'] = None
                row[f'Link Sesión {j}'] = None

            data.append(row)

        # Crear un DataFrame con los datos extraídos
        df = pd.DataFrame(data)

        # Mostrar el DataFrame en la consola
        if not df.empty:
            print(df)
            #df.to_csv('pepaciencia.csv', index=False, encoding='utf-8-sig')
        else:
            print("No se encontraron películas para el día de hoy.")
        return df
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

# Ejecutar el script
if __name__ == "__main__":
    scrape_circulo_bellas_artes()
