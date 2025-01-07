import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_teatro_lara():
    # URL de la página de teatro que vas a scrapear
    URL = 'https://entradas.teatrolara.com/entradas.teatrolara/events'
    
    # Agregar cabeceras para simular una solicitud desde un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    response = requests.get(URL, headers=headers)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen obras de teatro
        obras = soup.find_all('ob-catalog-card')  # Ajustar la etiqueta a la que está en el HTML

        data = []

        if obras:
            for obra in obras:
                # Extraer el título
                titulo_tag = obra.find('span', class_='title')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer la carátula
                imagen_tag = obra.find('img', alt='event image')
                imagen = imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                # Extraer el director
                director_tag = obra.find('span', class_='subtitle')
                director = director_tag.text.strip().replace('de ', '') if director_tag else 'Director no disponible'

                # Extraer las fechas de la sesión
                fechas_tag = obra.find('span', class_='ng-star-inserted')
                fechas = fechas_tag.text.strip() if fechas_tag else 'Fecha no disponible'

                # Extraer el enlace a la actividad
                event_id = obra['id'].split('-')[-1]  # Extraer el eventId de la etiqueta 'id'
                enlace = f"https://entradas.teatrolara.com/entradas.teatrolara/events/{event_id}?sessionView=LIST"

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
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_teatro_lara()
