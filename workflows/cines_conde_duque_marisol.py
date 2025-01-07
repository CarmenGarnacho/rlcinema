from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_conde_duque_morasol():
    # Configuración de Selenium y ChromeDriver
    options = Options()
    options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')  # Deshabilita la GPU
    options.add_argument('--no-sandbox')  # Necesario para algunos entornos
    options.add_argument('--disable-dev-shm-usage')  # Para evitar errores de memoria en entornos limitados

    # Inicializar el navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        URL = 'https://www.reservaentradas.com/cine/madrid/condeduqueauditoriomorasol/#sesioneshoy'
        driver.get(URL)

        # Esperar hasta que el contenedor de películas esté presente
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'movie')))
            print("Contenedor de películas encontrado.")
        except:
            print("No se encontró el contenedor de películas. Verifica la estructura de la página.")
            return pd.DataFrame()

        # Encontrar todas las películas
        peliculas = driver.find_elements(By.CLASS_NAME, 'movie')

        data = []
        for pelicula in peliculas:
            try:
                # Extraer el título de la película
                titulo = pelicula.find_element(By.CLASS_NAME, 'title-movie-list').find_element(By.TAG_NAME, 'a').text.strip()
            except:
                titulo = 'Título no disponible'

            try:
                # Extraer la duración
                duracion = pelicula.find_element(By.CLASS_NAME, 'glyphicon-time').find_element(By.XPATH, '..').text.strip()
            except:
                duracion = 'Duración no disponible'

            try:
                # Extraer la imagen (carátula)
                imagen = pelicula.find_element(By.TAG_NAME, 'img').get_attribute('src')
            except:
                imagen = 'Imagen no disponible'

            # Extraer las sesiones y sus enlaces de compra
            try:
                sesiones_container = pelicula.find_element(By.CLASS_NAME, 'sessions-list')
                sesiones = sesiones_container.find_elements(By.CLASS_NAME, 'session-container')
                sesiones_info = []
                for sesion in sesiones:
                    try:
                        hora = sesion.find_element(By.TAG_NAME, 'a').text.strip()
                        enlace_compra = sesion.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        # Validar sesiones con enlace y hora
                        if hora and enlace_compra and "Ver más" not in hora:
                            sesiones_info.append({
                                'hora': hora,
                                'enlace': enlace_compra
                            })
                    except:
                        continue
            except:
                sesiones_info = []

            # Añadir la película solo si tiene al menos una sesión válida
            if titulo != 'Título no disponible' and len(sesiones_info) > 0:
                row = {
                    'Carátula': imagen,
                    'Título': titulo,
                    'Duración': duracion
                }

                # Añadir las sesiones
                for i, sesion in enumerate(sesiones_info, start=1):
                    row[f'Sesión {i}'] = sesion['hora']
                    row[f'Link Sesión {i}'] = sesion['enlace']

                # Rellenar las sesiones vacías si hay menos de 5
                max_sesiones = len(sesiones_info)
                for i in range(max_sesiones + 1, 6):
                    row[f'Sesión {i}'] = None
                    row[f'Link Sesión {i}'] = None

                data.append(row)

        # Crear un DataFrame con los datos
        df = pd.DataFrame(data)
        return df

    finally:
        driver.quit()

# Si quieres probar el script directamente
if __name__ == "__main__":
    df_peliculas = scrape_conde_duque_morasol()
    if not df_peliculas.empty:
        print(df_peliculas)
