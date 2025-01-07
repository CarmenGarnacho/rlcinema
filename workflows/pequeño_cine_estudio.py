from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime

# Función para convertir la fecha de la sesión
def convertir_fecha_sesion(sesion):
    # Remover la letra del día de la semana (primera letra) y la 'h' de la hora
    dia_hora = sesion.strip()[1:].replace('h', '').strip()
    
    # Obtener el día y mes
    dia_mes = dia_hora.split('-')[0].strip()
    hora = dia_hora.split('-')[1].strip()

    # Mapear los días al número del mes
    try:
        fecha = datetime.strptime(dia_mes, '%d/%m')
        fecha = fecha.replace(year=2024)  # Añadimos el año 2024
        return fecha.strftime('%d/%m/%Y') + " " + hora
    except ValueError:
        return "Fecha no válida"

def scrape_pcine_estudio():
    # Configuración de Selenium para ejecutar en modo headless
    options = Options()
    options.add_argument('--headless')  # Ejecutar sin interfaz gráfica
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Mejora en sistemas con poca memoria compartida

    # Inicializar el navegador con ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL de la página del cine
    URL = 'https://www.pcineestudio.es/en-cartel'
    driver.get(URL)

    # Obtener el HTML de la página cargada
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Encontrar el script que contiene el JSON de las películas
    script_tag = soup.find('script', {'id': 'wix-warmup-data'})

    if not script_tag:
        print("No se encontró el script con los datos.")
        driver.quit()
        return pd.DataFrame()

    # Extraer el contenido del script
    json_data = json.loads(script_tag.string)

    # Acceder a los datos de las películas dentro de dataStore
    try:
        peliculas_data = json_data['appsWarmupData']['dataBinding']['dataStore']['recordsByCollectionId']['peliculas']
    except KeyError as e:
        print(f"Error al acceder a los datos: {e}")
        driver.quit()
        return pd.DataFrame()

    # Crear una lista para almacenar los datos de las películas
    data = []

    # Procesar cada película para extraer su información
    for pelicula_id, pelicula_info in peliculas_data.items():
        try:
            # Obtener los datos de la película
            titulo = pelicula_info.get('title', 'Título no disponible')
            director = pelicula_info.get('descripcinLarga', '').split('Dirección')[-1].split('\n')[0].strip() if 'Dirección' in pelicula_info.get('descripcinLarga', '') else 'Director no disponible'
            duracion = pelicula_info.get('descripcinCorta', '').split('Duración')[-1].split('min.')[0].strip() + ' min.' if 'Duración' in pelicula_info.get('descripcinCorta', '') else 'Duración no disponible'
            
            # Buscar la imagen (carátula) en el campo 'uri' y concatenar con la URL base
            imagen_uri = pelicula_info.get('cartel', None)
            imagen = f"https://static.wixstatic.com/media/{imagen_uri}" if imagen_uri else 'Imagen no disponible'

            # Extraer las sesiones
            sesiones_texto = pelicula_info.get('horario', 'Sesiones no disponibles').split('\n')
            sesiones_info = []
            for sesion in sesiones_texto:
                fecha_hora = convertir_fecha_sesion(sesion)
                sesiones_info.append({
                    'hora': fecha_hora,
                    'enlace': 'https://feverup.com/m/95546'  # Link común para todas las sesiones
                })

            # Crear una fila para el DataFrame
            row = {
                'Carátula': imagen,
                'Título': titulo,
                'Director': director,
                'Duración': duracion,
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

        except KeyError:
            print(f"Información no disponible para la película con ID: {pelicula_id}")

    # Crear un DataFrame con los datos
    df = pd.DataFrame(data)

    driver.quit()

    return df

# Si quieres probar el script directamente
if __name__ == "__main__":
    df = scrape_pcine_estudio()
    print(df)
