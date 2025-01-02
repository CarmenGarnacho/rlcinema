from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Asegúrate de importar Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def scrape_yelmo_ideal():
    # Configuración de Selenium y ChromeDriver para el entorno
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    chrome_options.add_argument('--disable-gpu')  # Deshabilita la GPU
    chrome_options.add_argument('--no-sandbox')  # Necesario para entornos sin privilegios
    chrome_options.add_argument('--disable-dev-shm-usage')  # Evita problemas de memoria en contenedores

    # Inicia el navegador Chrome con las opciones
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # URL de la página de cine que vas a scrapear
        URL = 'https://yelmocines.es/cartelera/madrid/ideal'
        driver.get(URL)

        # Esperar hasta que el elemento deseado esté presente (max 15 segundos)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'now__movie')))

        # Obtener el contenido HTML de la página
        html = driver.page_source

        # Parsear el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar todas las películas en la página
        peliculas = soup.find_all('article', class_='now__movie')

        data = []
        for pelicula in peliculas:
            # Extraer los horarios para verificar el enlace de compra
            horarios = pelicula.find_all('time', class_='btn')
            if not horarios:
                continue  # Si no hay horarios, saltar la película

            sesiones_info = []
            for horario in horarios:
                enlace = horario.find('a')['href'] if horario.find('a') else None
                # Verificar que el enlace contenga el ID del cine "Ideal" (780)
                if enlace and 'cinemaVistaId=780' not in enlace:
                    continue  # Si el enlace no es del cine Ideal, saltar esta sesión
                hora = horario.text.strip() if horario else 'Hora no disponible'
                sesiones_info.append({
                    'hora': hora,
                    'enlace': enlace
                })

            if not sesiones_info:
                continue  # Si no hay sesiones válidas, saltar la película

            # Extraer el título de la película
            titulo_tag = pelicula.find('h3')
            titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

            # Extraer la imagen de la película
            imagen_tag = pelicula.find('img')
            imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

            # Extraer la duración
            duracion_tag = pelicula.find('span', class_='duracion')
            duracion = duracion_tag.text.strip() + ' minutos' if duracion_tag else 'Duración no disponible'

            # Extraer la clasificación (versión) desde el div con clase "col3 cf"
            version_tag = pelicula.find('div', class_='col3 cf')
            version = version_tag.text.strip() if version_tag else 'Versión no disponible'

            # Extraer el director (no proporcionado en la fuente)
            director = 'Director no disponible'

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

        # Guardar el DataFrame en un archivo CSV
        # df.to_csv('cinesideal.csv', index=False)
        return df

    finally:
        driver.quit()  # Cerrar el navegador

# Si quieres probar el script directamente
if __name__ == "__main__":
    df_peliculas = scrape_yelmo_ideal()
    if not df_peliculas.empty:
        print(df_peliculas)
