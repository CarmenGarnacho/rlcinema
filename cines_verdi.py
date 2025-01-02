from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scrape_cines_verdi():
    # Configuración de Selenium y ChromeDriver para Heroku
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')  # Deshabilita la GPU
    options.add_argument('--no-sandbox')  # Necesario para entornos sin privilegios como Heroku
    options.add_argument('--disable-dev-shm-usage')  # Para evitar errores relacionados con la memoria compartida

    # Inicializar el navegador con Selenium
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Abrir la página
        URL = 'https://madrid.cines-verdi.com/cartelera'
        driver.get(URL)

        # Esperar hasta que el select de opciones esté disponible
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-select')))

        # Obtener el HTML de la página
        html = driver.page_source

        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar todas las películas en la cartelera
        peliculas = soup.find_all('article', class_='article-cartelera')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Verificar si la película tiene sesiones para "Hoy"
                select_tag = pelicula.find('select', class_='custom-select')
                if select_tag:
                    opciones = select_tag.find_all('option')
                    for opcion in opciones:
                        if 'Hoy' in opcion.text:  # Filtrar las opciones que son para "Hoy"
                            # Extraer el título de la película del <a> que contiene el enlace al título
                            titulo_tag = pelicula.find('a', href=True, title=True)
                            titulo = titulo_tag.get('title') if titulo_tag else 'Título no disponible'

                            # Extraer el director
                            director_tag = pelicula.find('th', string="DIRECTOR:").find_next('td')
                            director = director_tag.text.strip() if director_tag else 'Director no disponible'

                            # Extraer la duración
                            duracion_tag = pelicula.find('th', string="DURACIÓN:").find_next('td')
                            duracion = duracion_tag.text.strip() + ' min' if duracion_tag else 'Duración no disponible'

                            # Extraer la versión (por ejemplo, CASTELLANO, V.O. SUB. CASTELLANO)
                            version_tag = pelicula.find('div', class_='col-3').find('span')
                            version = version_tag.text.strip() if version_tag else 'Versión no disponible'

                            # Extraer la carátula (imagen)
                            imagen_tag = pelicula.find('img', class_='img-cartelera')
                            imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                            # Extraer las sesiones para "Hoy"
                            sesiones_info = []
                            sesiones = pelicula.find('div', class_='col-9 mb-2').find_all('a')  # Todas las sesiones de la película
                            for sesion in sesiones:
                                hora = sesion.text.strip() if sesion else 'Hora no disponible'
                                enlace_compra = sesion['href'] if sesion else 'Enlace no disponible'
                                sesiones_info.append({'hora': hora, 'enlace': enlace_compra})

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

                            # Completar con None si hay menos de 5 sesiones
                            max_sesiones = len(sesiones_info)
                            for i in range(max_sesiones + 1, 6):
                                row[f'Sesión {i}'] = None
                                row[f'Link Sesión {i}'] = None

                            data.append(row)
                            break  # Solo queremos las sesiones de "Hoy", romper el bucle aquí

            # Crear un DataFrame con los datos
            df = pd.DataFrame(data)

            # Imprimir el DataFrame
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
    scrape_cines_verdi()
