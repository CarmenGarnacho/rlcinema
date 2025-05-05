import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración de Selenium
def configurar_selenium():
    options = Options()
    options.add_argument('--headless')  # Ejecuta en modo headless (sin interfaz gráfica)
    options.add_argument('--disable-gpu')  # Deshabilita la GPU
    options.add_argument('--no-sandbox')  # Necesario para algunos entornos
    options.add_argument('--disable-dev-shm-usage')  # Evitar errores de memoria en entornos limitados
    
    driver = webdriver.Chrome(options=options)
    return driver

# Función para obtener las sesiones con fecha y hora desde la página de compra
def obtener_sesiones(url_compra):
    print(f"Accediendo a la página de sesiones en {url_compra}")
    
    # Iniciar Selenium
    driver = configurar_selenium()
    
    # Acceder a la URL de las sesiones
    driver.get(url_compra)
    
    # Esperar hasta que los botones de SESIONES estén presentes
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mi_but_background')))
    
    sesiones = []
    
    # Buscar todos los botones de "SESIONES"
    botones_sesiones = driver.find_elements(By.XPATH, "//input[contains(@value, 'SESIONES')]")
    
    for index, boton in enumerate(botones_sesiones):
        try:
            # Reubicar los botones de sesión si es necesario
            botones_sesiones = driver.find_elements(By.XPATH, "//input[contains(@value, 'SESIONES')]")
            if index >= len(botones_sesiones):
                print(f"Índice fuera de rango: {index}, total de botones: {len(botones_sesiones)}")
                continue  # Saltar si el índice está fuera de rango

            boton_actual = botones_sesiones[index]
            
            # Guardar la fecha antes de hacer clic
            fecha_element = boton_actual.find_element(By.XPATH, "../preceding-sibling::div[1]//span[@style='font-size:medium;']")
            fecha = fecha_element.text if fecha_element else "Fecha no disponible"
            
            # Hacer clic en el botón "SESIONES"
            boton_actual.click()
            time.sleep(2)  # Esperar a que la hora se despliegue
            
            # Buscar la hora desplegada
            horas = driver.find_elements(By.XPATH, "//input[@class='btn btn-info']")
            
            for hora in horas:
                sesiones.append({'Fecha': fecha, 'Hora': hora.get_attribute("value")})
            
            # Volver a la página anterior sin usar driver.back(), directamente recargando la página inicial
            driver.get(url_compra)
            time.sleep(2)  # Esperar a que la página recargue
        
        except Exception as e:
            print(f"Error al procesar la sesión: {str(e)}")
    
    driver.quit()
    return sesiones

# Función para obtener la información detallada de la película desde la página de detalle
def obtener_info_detalle(url_detalle):
    print(f"Accediendo a la página de detalle en {url_detalle}")
    try:
        response = requests.get(url_detalle)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraer la descripción corta (director, duración y versión)
            short_description = soup.find('div', class_='shortDescription')
            director, version, duracion = 'Director no disponible', 'Versión no disponible', 'Duración no disponible'
            
            if short_description:
                info = short_description.find_all('p')
                
                # Recorrer párrafos para encontrar la versión y duración
                for i in range(len(info)):
                    if 'min' in info[i].text:  # Si contiene 'min', es la duración y posiblemente la versión
                        duracion = info[i].text.split(' – ')[-1].strip()  # Duración después del guion
                        if 'VOSE' in info[i].text:
                            version = 'Digital – VOSE'
                        elif 'VO' in info[i].text:
                            version = 'Digital – VO'
                        else:
                            version = 'Versión no disponible'
                        
                        # El director está en el párrafo anterior
                        if i > 0:
                            director = info[i-1].text.split(' / ')[0].strip() if ' / ' in info[i-1].text else 'Director no disponible'
                        break

            # Extraer el enlace de compra
            comprar_link = soup.find('a', class_='submit')
            link_compra = comprar_link['href'] if comprar_link and 'href' in comprar_link.attrs else 'Link de compra no disponible'

            # Si se encuentra el enlace de compra, extraer las sesiones
            sesiones = obtener_sesiones(link_compra) if link_compra != 'Link de compra no disponible' else []

            return director, version, duracion, link_compra, sesiones
        else:
            print(f"Error al acceder a la página de detalle: {response.status_code}")
            return 'Director no disponible', 'Versión no disponible', 'Duración no disponible', 'Link de compra no disponible', []
    except Exception as e:
        print(f"Error durante la extracción de la página de detalle: {str(e)}")
        return 'Director no disponible', 'Versión no disponible', 'Duración no disponible', 'Link de compra no disponible', []

# Función principal para scrapear la página de listado de películas y obtener detalles
def scrape_sala_equis():
    base_url = 'https://salaequis.es/taquilla/'
    print(f"Accediendo a la página principal: {base_url}")

    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Lista para almacenar la información de las películas
        data = []

        # Encontrar todas las filas de películas
        peliculas = soup.find_all('div', class_='row')

        if peliculas:
            for pelicula in peliculas:
                # Inicializar variables por defecto
                titulo = 'Título no disponible'
                enlace_detalle = None
                caratula = '/static/images/sincaratula.jpg'

                # Extraer el título y el enlace de detalle
                titulo_tag = pelicula.find('div', class_='title')
                if titulo_tag:
                    a_tag = titulo_tag.find('a')
                    if a_tag:
                        titulo = a_tag.text.strip()
                        enlace_detalle = a_tag['href']

                # Extraer la carátula
                imagen_tag = pelicula.find('div', class_='image')
                if imagen_tag:
                    img_tag = imagen_tag.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        caratula = img_tag['src']

                # Si hay enlace de detalle, extraemos la información adicional
                if enlace_detalle:
                    director, version, duracion, link_compra, sesiones = obtener_info_detalle(enlace_detalle)
                else:
                    director, version, duracion, link_compra, sesiones = 'Director no disponible', 'Versión no disponible', 'Duración no disponible', 'Link de compra no disponible', []

                # Crear una fila para el DataFrame
                row = {
                    'Carátula': caratula,
                    'Título': titulo,
                    'Director': director,
                    'Duración': duracion,
                    'Versión': version
                }

                # Añadir sesiones a la fila con formato Fecha Hora
                for i, sesion in enumerate(sesiones, start=1):
                    row[f'Sesión {i}'] = f"{sesion['Fecha']} {sesion['Hora']}" if 'Fecha' in sesion and 'Hora' in sesion else None
                    row[f'Link Sesión {i}'] = link_compra if link_compra != 'Link de compra no disponible' else None

                # Rellenar el resto de las columnas de sesión si hay menos de 5
                max_sesiones = len(sesiones)
                for i in range(max_sesiones + 1, 6):
                    row[f'Sesión {i}'] = None
                    row[f'Link Sesión {i}'] = None

                data.append(row)

        # Crear un DataFrame con los datos
        df = pd.DataFrame(data)

        # Imprimir el DataFrame para verificar los datos
        print(df)
        df.to_csv('salaequis.csv', index=False, encoding='utf-8-sig')
        return df
    else:
        print(f"Error al acceder a la página principal: {response.status_code}")
        return pd.DataFrame()

# Ejecutar la función
scrape_sala_equis()
