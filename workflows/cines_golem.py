from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def scrape_golem_madrid():
    # Configuración de Selenium y ChromeDriver para Heroku
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    chrome_options.add_argument('--disable-gpu')  # Deshabilita la GPU
    chrome_options.add_argument('--no-sandbox')  # Necesario para entornos sin privilegios como Heroku
    chrome_options.add_argument('--disable-dev-shm-usage')  # Evita problemas de memoria en contenedores

    # Inicia el navegador Chrome con las opciones
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # URL de la página de cine que vas a scrapear
        URL = 'https://www.golem.es/golem/golem-madrid'
        driver.get(URL)

        # Esperar hasta que el elemento deseado esté presente (max 10 segundos)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td[bgcolor="#E5E5E5"]')))

        # Obtener el contenido HTML de la página
        html = driver.page_source

        # Parsear el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar todas las secciones de películas
        peliculas = soup.find_all('td', {'bgcolor': '#E5E5E5'})

        if not peliculas:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()

        data = []
        for pelicula in peliculas:
            try:
                # Extraer el título de la película
                titulo_tag = pelicula.find('a', class_='txtNegXXL')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'
            except:
                titulo = 'Título no disponible'

            # Buscar la siguiente fila para extraer la imagen y más información
            try:
                contenedor_imagen = pelicula.find_next('tr')
                imagen_tag = contenedor_imagen.find('img', class_='bordeCartel')
                imagen = 'https://www.golem.es' + imagen_tag['src'] if imagen_tag else 'Imagen no disponible'
            except:
                imagen = 'Imagen no disponible'

            # Versión de la película
            try:
                version = titulo.split('(')[-1].replace(')', '').strip() if '(' in titulo else 'Versión no disponible'
            except:
                version = 'Versión no disponible'

            # Para seguir el formato, asignamos valores predeterminados para Director y Duración
            director = 'Director no disponible'
            duracion = 'Duración no disponible'

            # Extraer el enlace de más información
            try:
                enlace_info_tag = contenedor_imagen.find('a', string='+ información')
                enlace_info = 'https://www.golem.es' + enlace_info_tag['href'] if enlace_info_tag else 'Enlace no disponible'
            except:
                enlace_info = 'Enlace no disponible'

            # Extraer las sesiones
            sesiones_info = []
            try:
                sesiones_tags = contenedor_imagen.find_all('table', {'width': '75'})
                for sesion_tag in sesiones_tags:
                    hora_tag = sesion_tag.find('a', class_='horaXXXL')
                    enlace_tag = sesion_tag.find('a', class_='horaTexto')

                    hora = hora_tag.text.strip() if hora_tag else 'Hora no disponible'
                    enlace_compra = 'https://www.golem.es' + enlace_tag['href'] if enlace_tag else 'Enlace no disponible'

                    sesiones_info.append({
                        'hora': hora,
                        'enlace': enlace_compra
                    })
            except:
                sesiones_info = []

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
        return df

    finally:
        driver.quit()  # Cerrar el navegador

# Si quieres probar el script directamente
if __name__ == "__main__":
    df_peliculas = scrape_golem_madrid()
    if not df_peliculas.empty:
        print(df_peliculas)