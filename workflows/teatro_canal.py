import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_teatros_canal():
    # URL de la página de teatro que vas a scrapear
    URL = 'https://www.teatroscanal.com/entradas/teatro-madrid/'
    base_url = 'https://www.teatroscanal.com'
    response = requests.get(URL)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen las obras de teatro
        obras = soup.find_all('div', class_='tribe-events-event')

        data = []

        # Definir títulos que se deben excluir
        titulos_excluir = ["PROGRAMACIÓN 2024 – 2025", "ABONOS TEATROS DEL CANAL"]

        if obras:
            for obra in obras:
                # Extraer el título de la obra
                titulo_tag = obra.find('h2', class_='show-home')
                titulo = titulo_tag.text.strip() if titulo_tag else None

                # Extraer la carátula
                imagen_tag = obra.find('img')
                imagen = imagen_tag['src'] if imagen_tag else None

                # Verificación para saltar las entradas sin título o sin carátula
                if not titulo or not imagen:
                    continue  # Saltar esta iteración si no hay título o carátula

                # Si el título está en la lista de exclusiones, lo saltamos
                if titulo in titulos_excluir:
                    continue  # Saltar esta iteración si el título está en la lista de exclusiones

                # Extraer el director
                director_tag_container = obra.find('div', class_='autor-show')
                if director_tag_container:
                    director_tag = director_tag_container.find('p')
                    director = director_tag.text.strip() if director_tag else 'Director no disponible'
                else:
                    director = 'Director no disponible'

                # Extraer las fechas de la sesión
                fechas_container = obra.find('div', class_='fecha-show')
                if fechas_container:
                    fechas_tag = fechas_container.find('p')
                    fechas = fechas_tag.text.strip() if fechas_tag else 'Fecha no disponible'
                else:
                    fechas = 'Fecha no disponible'

                # Extraer el enlace de compra de entradas
                enlace_tag = obra.find('a', class_='boton_comprar')
                enlace = enlace_tag['href'] if enlace_tag else 'Enlace no disponible'

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
    scrape_teatros_canal()
