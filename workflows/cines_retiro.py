import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_cines_retiro():
    # URL de la página de cine que vas a scrapear
    URL = 'https://www.cinesrenoir.com/cine/renoir-retiro/cartelera/'
    response = requests.get(URL)

    # Verifica si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las secciones que contienen películas
        peliculas = soup.find_all('div', class_='col-9 pl-0 pr-0')

        data = []

        if peliculas:
            for pelicula in peliculas:
                # Extraer el título
                titulo_tag = pelicula.find('a')
                titulo = titulo_tag.text.strip() if titulo_tag else 'Título no disponible'

                # Extraer el director (mismo estilo de las otras páginas)
                director_tag = pelicula.find('small', style="color:#748294")
                director = director_tag.text.strip().replace('de ', '') if director_tag else 'Director no disponible'

                # Extraer la duración (nueva lógica)
                duracion_tag = pelicula.find_all('small', style="color:#748294")
                duracion = None
                for tag in duracion_tag:
                    if 'Duración' in tag.text:
                        duracion = tag.text.strip().split('Duración ')[-1].split()[0] + ' minutos'
                        break
                duracion = duracion if duracion else 'Duración no disponible'

                # Extraer la carátula (imagen) de la película
                imagen_tag = pelicula.find_previous_sibling('div', class_='col-3 pl-0')
                imagen = imagen_tag.find('img')['src'] if imagen_tag and imagen_tag.find('img') else 'Imagen no disponible'

                # Extraer la versión (VOS, VOSE, etc.)
                version_tags = pelicula.find_all('small')
                version = version_tags[1].text.strip() if len(version_tags) > 1 else 'Versión no disponible'

                # Extraer las sesiones
                sesiones = pelicula.find_all('div', class_='text-center')
                sesiones_info = []
                for sesion in sesiones:
                    sala_tag = sesion.find('span', style="font-size:12px")
                    sala = sala_tag.text.strip() if sala_tag else 'Sala no disponible'
                    hora_tag = sesion.find('a')
                    hora = hora_tag.text.strip() if hora_tag else 'Hora no disponible'
                    enlace_compra = hora_tag['href'] if hora_tag and 'href' in hora_tag.attrs else 'Enlace no disponible'
                    sesiones_info.append({
                        'sala': sala,
                        'hora': hora,
                        'enlace': enlace_compra
                    })

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

            # Imprimir el DataFrame
            print(df)
            return df
        else:
            print("No se encontraron películas en la página.")
            return pd.DataFrame()
    else:
        print(f"Error al conectarse a la página web: {response.status_code}")
        return pd.DataFrame()

# Si quieres probar el script directamente
if __name__ == "__main__":
    scrape_cines_retiro()
