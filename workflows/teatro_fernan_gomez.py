import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_teatro_fernangomez():
    # URL de la página de teatro que vas a scrapear
    URL = 'https://www.teatrofernangomez.es/programacion/teatro'
    base_url = 'https://www.teatrofernangomez.es'
    
    # Añadir encabezados para simular que la solicitud proviene de un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(URL, headers=headers)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen las obras de teatro
        obras = soup.find_all('div', class_='node--view-mode-destacados-home')

        data = []

        # Definir las palabras clave para excluir los títulos
        excluidos = ["Programación Temporada 2024 / 2025", "Encuentros", "Actividades"]

        if obras:
            for obra in obras:
                # Extraer el título de la obra
                titulo_tag = obra.find('div', class_='field-name-node-title').find('h2')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Si el título contiene alguna palabra clave de exclusión, saltarlo
                if any(excluido.lower() in titulo.lower() for excluido in excluidos):
                    continue  # Saltar esta iteración si el título debe ser excluido

                # Extraer la carátula (imagen)
                imagen_tag = obra.find('img')
                imagen = base_url + imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                # Extraer el director (después de "dirección:")
                director_tag = obra.find('div', class_='field--name-field-subtitle')
                director = 'Director no disponible'
                if director_tag:
                    texto_director = director_tag.text.strip()
                    if 'dirección:' in texto_director.lower():
                        director = texto_director.split('dirección:')[-1].strip()

                # Extraer las fechas de la sesión
                fechas_tag = obra.find('div', class_='field--name-field-schedule-tip')
                fechas = fechas_tag.text.strip() if fechas_tag else 'Fechas no disponibles'

                # Construir el enlace completo a la obra
                enlace_tag = obra.find('a', class_='field-group-link')
                enlace = base_url + enlace_tag['href'] if enlace_tag else 'Enlace no disponible'

                # Verificar si la obra ya está en la lista
                obra_existente = next((item for item in data if item['Título'] == titulo), None)
                
                if obra_existente:
                    # Si la obra ya existe, añadir la nueva sesión
                    num_sesiones = sum(1 for key in obra_existente if key.startswith('Sesión')) + 1
                    obra_existente[f'Sesión {num_sesiones}'] = fechas
                    obra_existente[f'Link Sesión {num_sesiones}'] = enlace
                else:
                    # Crear una fila para el DataFrame si la obra no está en la lista
                    row = {
                        'Carátula': imagen,
                        'Título': titulo,
                        'Director': director,
                        'Duración': 'Duración no disponible',
                        'Versión': 'Versión no disponible',
                        'Sesión 1': fechas,
                        'Link Sesión 1': enlace
                    }

                    # Añadir la fila a los datos
                    data.append(row)

            # Crear un DataFrame con los datos
            df = pd.DataFrame(data)

            # Rellenar el resto de las columnas de sesión si hay menos de 5 por obra
            for row in data:
                max_sesiones = sum(1 for key in row if key.startswith('Sesión'))
                for i in range(max_sesiones + 1, 6):
                    row[f'Sesión {i}'] = None
                    row[f'Link Sesión {i}'] = None

            # Mostrar el DataFrame
            df = pd.DataFrame(data)
            print(df)
            return df
        else:
            print("No se encontraron obras en la página.")
            return pd.DataFrame()
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_teatro_fernangomez()
