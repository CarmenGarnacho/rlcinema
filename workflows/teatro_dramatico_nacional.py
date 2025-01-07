from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

def extraer_director(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Buscar las variantes de "Dirección" en el texto y extraer el nombre del director
    for p in soup.find_all('p'):
        if 'Dirección' in p.get_text() or 'Adaptación y dirección' in p.get_text() or 'Texto y dirección' in p.get_text():
            return p.get_text().split('Dirección')[-1].strip()  # Extraer después de 'Dirección'
    return 'Director no disponible'

def extraer_fechas(html):
    # Usamos BeautifulSoup para parsear y extraer el texto de las fechas
    soup = BeautifulSoup(html, 'html.parser')
    for p in soup.find_all('p'):
        # El patrón de fechas siempre parece seguir este formato: "dd MMM - dd MMM"
        if '-' in p.get_text():
            # Extraer las fechas que están antes del símbolo '|'
            fechas = p.get_text().split('|')[0].strip()
            return fechas
    return 'Fechas no disponibles'

def scrape_dramatico_teatro():
    # Configuración de Selenium y ChromeDriver
    options = Options()
    options.add_argument('--disable-gpu')  # Deshabilita la GPU
    options.add_argument('--no-sandbox')  # Necesario para algunos entornos
    options.add_argument('--disable-dev-shm-usage')  # Para evitar errores relacionados con la memoria
    options.add_argument('--disable-software-rasterizer')  # Desactiva la rasterización por software

    # Inicializar el navegador con estas opciones
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # URL de la página que vas a scrapear
        URL = 'https://dramatico.mcu.es/'
        driver.get(URL)

        # Aumentar el tiempo de espera para rellenar el CAPTCHA manualmente
        print("Por favor, rellena el CAPTCHA manualmente si aparece.")
        time.sleep(60)  # Ajusta según sea necesario

        # Desplazarse hacia abajo para cargar todo el contenido después de rellenar el CAPTCHA
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Encontrar todas las secciones que contienen obras de teatro
        obras = driver.find_elements(By.CLASS_NAME, 'item-event-resume')

        data = []

        if obras:
            for obra in obras:
                # Extraer el título
                try:
                    titulo = obra.find_element(By.TAG_NAME, 'h2').text.strip()
                    # Excluir títulos como "Pases del #Dramático"
                    if titulo == "Pases del #Dramático":
                        continue
                except:
                    titulo = 'Título no disponible'

                # Extraer la carátula
                try:
                    imagen = obra.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except:
                    imagen = 'Imagen no disponible'

                # Extraer el texto donde aparece la dirección
                try:
                    detalles_tag = obra.find_element(By.CLASS_NAME, 'detail').get_attribute('innerHTML')
                    director = extraer_director(detalles_tag)
                except:
                    director = 'Director no disponible'

                # Extraer las fechas de la sesión
                try:
                    detalles_tag = obra.find_element(By.CLASS_NAME, 'detail').get_attribute('innerHTML')
                    fechas = extraer_fechas(detalles_tag)
                except:
                    fechas = 'Fechas no disponibles'

                # Extraer el enlace de las entradas
                try:
                    enlace = obra.find_element(By.CLASS_NAME, 'border-outline').get_attribute('href')
                except:
                    enlace = 'Enlace no disponible'

                # Crear una fila para el DataFrame
                row = {
                    'Carátula': imagen,
                    'Título': titulo,
                    'Director': director,
                    'Duración': 'Duración no disponible',
                    'Versión': 'Versión no disponible'
                }

                # Crear la información de las sesiones
                sesiones_info = [
                    {
                        'hora': fechas,
                        'enlace': enlace
                    }
                ]

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
            print("No se encontraron obras en la página.")
            return pd.DataFrame()
    finally:
        # Cerrar el navegador
        driver.quit()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_dramatico_teatro()
