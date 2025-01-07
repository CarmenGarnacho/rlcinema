from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from webdriver_manager.chrome import ChromeDriverManager

def scrape_timeout_exposiciones():
    # Configuración de Selenium y ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')  # Deshabilita la GPU
    options.add_argument('--no-sandbox')  # Necesario para entornos sin privilegios
    options.add_argument('--disable-dev-shm-usage')  # Para evitar errores de memoria compartida

    # Inicializar el navegador
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Abrir la página principal
        URL = 'https://www.timeout.es/madrid/es/arte/exposiciones-en-madrid-el-arte-que-no-te-puedes-perder'
        driver.get(URL)

        # Esperar hasta que el contenido esté disponible
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.articleContent')))

        # Obtener el HTML de la página
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar todas las exposiciones
        exposiciones = soup.find_all('div', class_='articleContent')

        data = []

        if exposiciones:
            for exposicion in exposiciones:
                # Extraer el link intermedio para obtener más detalles
                link_tag = exposicion.find('a', class_='tileImageLink', href=True)
                link = "https://www.timeout.es" + link_tag['href'] if link_tag else None

                # Definir variables para el scraping del enlace intermedio
                titulo, imagen, descripcion, lugar, fechas, precio, entradas = 'Título no disponible', 'Imagen no disponible', 'Descripción no disponible', 'Lugar no disponible', 'Fechas no disponibles', 'Precio no disponible', 'Entradas no disponibles'

                if link:
                    # Abrir la página del enlace intermedio para obtener más detalles
                    driver.get(link)
                    sub_html = driver.page_source
                    sub_soup = BeautifulSoup(sub_html, 'html.parser')

                    # Extraer el título de la exposición desde el h1
                    titulo_tag = sub_soup.find('h1', class_='_h1_1ucvn_1')
                    titulo = titulo_tag.get_text(strip=True) if titulo_tag else 'Título no disponible'

                    # Extraer la carátula de la exposición (imagen)
                    imagen_tag = sub_soup.find('img', {'data-testid': 'responsive-image_testID'})
                    imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                    # Extraer la descripción
                    descripcion_tag = sub_soup.find('div', id='content')
                    descripcion = descripcion_tag.get_text(strip=True) if descripcion_tag else 'Descripción no disponible'

                    # Extraer el lugar (buscar el <li> que contiene un lugar, no la categoría "Arte")
                    lugar_tags = sub_soup.find_all('li', class_='_tag_14748_12')
                    lugar = 'Lugar no disponible'

                    # Recorrer las etiquetas <li> y encontrar el que tenga el texto adecuado
                    for lugar_tag in lugar_tags:
                        lugar_span = lugar_tag.find('span', class_='_text_14748_41')
                        if lugar_span and "Arte" not in lugar_span.get_text(strip=True):  # Excluir "Arte"
                            lugar = lugar_span.get_text(strip=True)
                            break

                    # Extraer las fechas
                    fechas_tag = sub_soup.find('time', class_='_time_t1na9_1')
                    fechas = fechas_tag.get_text(strip=True) if fechas_tag else 'Fechas no disponibles'

                    # Extraer el precio
                    precio_tag = sub_soup.find('div', class_='_price_1ssr8_49')
                    precio = precio_tag.get_text(strip=True) if precio_tag else 'Precio no disponible'

                    # Extraer el enlace de entradas
                    entradas_tag = sub_soup.find('a', class_='contact-website')
                    entradas = entradas_tag['href'] if entradas_tag else 'Entradas no disponibles'

                # Crear una fila de datos para el JSON
                row = {
                    'Carátula Exposición': imagen,
                    'Exposición': titulo,
                    'Descripción': descripcion,
                    'Lugar': lugar,
                    'Fechas': fechas,
                    'Precio': precio,
                    'Entradas': entradas
                }

                data.append(row)

            # Guardar los datos en formato JSON sin caracteres especiales
            with open('exposiciones.json', 'w', encoding='utf-8', newline='\n') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"Se ha generado el archivo exposiciones.json con {len(data)} exposiciones.")
            return data
        else:
            print("No se encontraron exposiciones en la página.")
            return []

    finally:
        # Cerrar el navegador
        driver.quit()

# Si deseas probar el script directamente
if __name__ == "__main__":
    scrape_timeout_exposiciones()

