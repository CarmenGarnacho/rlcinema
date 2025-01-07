import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_nave10_teatro():
    # URL de la página de teatro que vas a scrapear
    URL = 'https://www.nave10matadero.es/programacion'
    base_url = 'https://www.nave10matadero.es'
    response = requests.get(URL)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen obras de teatro
        obras = soup.find_all('article', class_='node--type-activity')

        data = []

        if obras:
            for obra in obras:
                # Extraer el título
                titulo_tag = obra.find('h3')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer la carátula
                imagen_tag = obra.find('img')
                imagen = base_url + imagen_tag['src'] if imagen_tag else 'Imagen no disponible'

                # Extraer el director
                director_tag = obra.find('div', class_='field--name-field-subtitle')
                director = director_tag.text.strip().replace('de ', '') if director_tag else 'Director no disponible'

                # Extraer las fechas de la sesión
                fecha_inicio_tag = obra.find('div', class_='field--name-field-init-date')
                fecha_fin_tag = obra.find('div', class_='field--name-field-end-date')

                fecha_inicio = fecha_inicio_tag.text.strip() if fecha_inicio_tag else 'Fecha no disponible'
                fecha_fin = fecha_fin_tag.text.strip() if fecha_fin_tag else 'Fecha no disponible'

                # Extraer el link a la actividad
                enlace_tag = obra.find('a', class_='field-group-link')
                enlace = base_url + enlace_tag['href'] if enlace_tag else 'Enlace no disponible'

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
                        'hora': f'{fecha_inicio} - {fecha_fin}',
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
    scrape_nave10_teatro()
