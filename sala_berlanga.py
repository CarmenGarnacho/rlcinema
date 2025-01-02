from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import locale

# Establecer la localización en español para manejar correctamente los nombres de meses
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def scrape_sala_berlanga():
    # Configuración de Selenium y ChromeDriver para lanzar el navegador
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # Quitar esta línea si deseas ver el navegador

    # Inicializar el navegador con Selenium
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Abrir la página
        URL = 'https://salaberlanga.com/programacion-de-actividades/'
        driver.get(URL)

        # Aumentar el tiempo de espera hasta 20 segundos para asegurar que la página cargue
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'card'))
        )

        # Obtener el HTML de la página
        html = driver.page_source

        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar todas las actividades
        peliculas = soup.find_all('div', class_='card')

        data = []

        # Obtener la fecha actual en el formato correcto
        hoy = datetime.now().day  # Día del mes sin cero inicial
        mes_actual = datetime.now().strftime("%B").lower()  # Ejemplo: "septiembre"
        hoy_str = f"{hoy} de {mes_actual}"

        if peliculas:
            for pelicula in peliculas:
                # Extraer el título de la película
                titulo_tag = pelicula.find('h5', class_='card-title')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer la carátula (imagen)
                imagen_tag = pelicula.find('img', class_='img-fluid')
                imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                # Extraer el director y la duración
                info_tag = pelicula.find('p', class_='card-text-time')
                if info_tag:
                    info_text = info_tag.text.strip()
                    director, _, duracion = info_text.partition('|')
                    director = director.strip()

                    # Extraer solo la parte de los minutos en la duración
                    duracion = duracion.strip().split('|')[-1].strip() if "|" in duracion else duracion.strip()
                    duracion = duracion.replace('´', ' min')  # Usamos la duración real
                else:
                    director = 'Director no disponible'
                    duracion = 'Duración no disponible'

                # Extraer las sesiones
                sesiones_tag = pelicula.find('p', class_='card-text-date')
                sesiones_info = []
                if sesiones_tag:
                    # Reemplazamos <br> por un espacio para que se procese bien
                    sesiones = sesiones_tag.decode_contents().replace('<br/>', '\n').replace('<br>', '\n').split('\n')
                    for sesion in sesiones:
                        sesion_info = sesion.strip().lower()
                        if hoy_str in sesion_info:
                            # Extraer solo la hora para la sesión de hoy
                            hora = sesion_info.split('-')[-1].strip()
                            sesiones_info.append({'hora': hora, 'enlace': 'Enlace no disponible'})  # Puedes ajustar si el enlace es diferente

                # Extraer el enlace de compra
                link_tag = pelicula.find('a', href=True, string="Entradas disponibles")
                enlace_compra = link_tag['href'] if link_tag else 'Enlace no disponible'

                if sesiones_info:  # Solo agregamos si hay sesiones del día de hoy
                    # Crear una fila para el DataFrame con la estructura que necesitas
                    row = {
                        'Carátula': imagen,
                        'Título': titulo,
                        'Director': director,
                        'Duración': duracion,  # Usamos solo la duración en minutos
                        'Versión': 'Versión no disponible'  # La versión sigue siendo no disponible ya que no tenemos ese dato
                    }

                    # Añadir sesiones a la fila
                    for i, sesion in enumerate(sesiones_info, start=1):
                        row[f'Sesión {i}'] = sesion['hora']
                        row[f'Link Sesión {i}'] = enlace_compra  # Asignamos el mismo enlace para todas las sesiones

                    # Rellenar el resto de las columnas de sesión si hay menos de 5
                    max_sesiones = len(sesiones_info)
                    for i in range(max_sesiones + 1, 6):
                        row[f'Sesión {i}'] = None
                        row[f'Link Sesión {i}'] = None

                    data.append(row)

            # Crear un DataFrame con los datos
            df = pd.DataFrame(data)

            # Imprimir el DataFrame filtrado
            print("Películas y sesiones filtradas para el día de hoy:")
            print(df)

            return df
        else:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()

    finally:
        # Cerrar el navegador
        driver.quit()

# Si deseas probar el script directamente
if __name__ == "__main__":
    scrape_sala_berlanga()
