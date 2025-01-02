from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_teatro_espanol_selenium():
    # Configuración de Selenium y ChromeDriver para Heroku
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    chrome_options.add_argument('--disable-gpu')  # Deshabilita la GPU
    chrome_options.add_argument('--no-sandbox')  # Necesario para entornos sin privilegios como Heroku
    chrome_options.add_argument('--disable-dev-shm-usage')  # Evita problemas de memoria en contenedores

    # Inicia el navegador Chrome con las opciones configuradas (sin especificar Service)
    driver = webdriver.Chrome(options=chrome_options)

    # Navegar a la página del teatro
    URL = 'https://www.teatroespanol.es/programacion'
    driver.get(URL)

    # Scroll para cargar más obras (scroll infinito)
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Desplazarse hacia abajo hasta el final de la página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Esperar un poco para que se cargue el contenido

        # Calcular la nueva altura de la página y comparar con la anterior
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Si no hay más cambios en la altura, salimos del bucle
        last_height = new_height

    # Extraer el contenido de la página con BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Encontrar todas las secciones que contienen obras de teatro
    obras = soup.find_all('div', class_='views-row')

    data = []

    if obras:
        for obra in obras:
            # Extraer el título
            titulo_tag = obra.find('span', class_='title')
            if not titulo_tag:  # Si no hay título, saltamos a la siguiente obra
                continue
            
            enlace_tag = titulo_tag.find('a')
            titulo = enlace_tag.text.strip() if enlace_tag else 'Título no disponible'
            enlace_obra = 'https://www.teatroespanol.es' + enlace_tag['href'] if enlace_tag else 'Enlace no disponible'

            # Extraer la carátula
            imagen_tag = obra.find('picture')
            if imagen_tag:
                imagen = 'https://www.teatroespanol.es' + imagen_tag.find('img')['src'] if imagen_tag.find('img') else 'Imagen no disponible'
            else:
                imagen = 'Imagen no disponible'

            # Extraer el director
            director_tag = obra.find('div', class_='field--name-field-secondary-subtitle')
            director = director_tag.text.strip() if director_tag else 'Director no disponible'

            # Extraer las fechas de la sesión
            fechas_tag = obra.find_all('div', class_='date')
            if len(fechas_tag) >= 2:
                fecha_inicio = fechas_tag[0].text.strip()
                fecha_fin = fechas_tag[1].text.strip()
                fechas = f'{fecha_inicio} - {fecha_fin}'
            else:
                fechas = 'Fechas no disponibles'

            # Extraer el link para comprar entradas
            enlace_entradas_tag = obra.find('div', class_='field-name-field-ticketing-links')
            if enlace_entradas_tag and enlace_entradas_tag.find('a'):
                enlace_entradas = enlace_entradas_tag.find('a')['href']
            else:
                enlace_entradas = 'Enlace no disponible'

            # Crear una fila para el DataFrame
            row = {
                'Carátula': imagen,
                'Título': titulo,
                'Director': director,
                'Duración': 'Duración no disponible',
                'Versión': 'Versión no disponible',
                'Sesión 1': fechas,
                'Link Sesión 1': enlace_entradas
            }

            # Añadir la fila a la lista de datos
            data.append(row)

        # Crear un DataFrame con los datos
        df = pd.DataFrame(data)

        # Imprimir el DataFrame
        print(df)
        df.to_csv('spanyol.csv', index=False, encoding='utf-8-sig')
        return df
    else:
        print("No se encontraron obras en la página.")
        return pd.DataFrame()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_teatro_espanol_selenium()
