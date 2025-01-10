import pandas as pd
import json
import os
from datetime import datetime
from cines_embajadores import scrape_cines_embajadores
from cines_plaza_espana import scrape_cines_plaza_espana
from cines_princesa import scrape_cines_princesa
from cines_retiro import scrape_cines_retiro
from cines_conde_duque_marisol import scrape_conde_duque_morasol
from filmoteca import scrape_filmoteca
from cines_golem import scrape_golem_madrid
from cineteca import scrape_cineteca_programacion
from cines_verdi import scrape_cines_verdi
# from artistic_metropol import scrape_artistic_metropol
from CBA import scrape_circulo_bellas_artes
from sala_berlanga import scrape_sala_berlanga
from cines_ideal import scrape_yelmo_ideal


def obtener_cartelera_combinada():
    # Llama a las funciones para obtener DataFrames
    df_embajadores = scrape_cines_embajadores()
    df_embajadores['Cine'] = 'Cines Embajadores'

    df_plaza_espana = scrape_cines_plaza_espana()
    df_plaza_espana['Cine'] = 'Cines Plaza España'

    df_princesa = scrape_cines_princesa()
    df_princesa['Cine'] = 'Cines Princesa'

    df_retiro = scrape_cines_retiro()
    df_retiro['Cine'] = 'Cines Retiro'

    df_filmoteca = scrape_filmoteca()
    df_filmoteca['Cine'] = 'Filmoteca'

    df_marisol = scrape_conde_duque_morasol()
    df_marisol['Cine'] = 'Cines Conde Duque Marisol'

    df_cineteca = scrape_cineteca_programacion()
    df_cineteca['Cine'] = 'Cineteca'

    df_verdi = scrape_cines_verdi()
    df_verdi['Cine'] = 'Cines Verdi'

    # df_metropol = scrape_artistic_metropol()
    # df_metropol['Cine'] = 'Artistic Metropol'

    df_CBA = scrape_circulo_bellas_artes()
    df_CBA['Cine'] = 'CBA'

    df_berlanga = scrape_sala_berlanga()
    df_berlanga['Cine'] = 'Sala Berlanga'

    df_ideal = scrape_yelmo_ideal()
    df_ideal['Cine'] = 'Cines Ideal'

    # Limpiar películas de Conde Duque Marisol
    def limpiar_conde_duque_marisol(df_marisol):
        for i in range(1, 6):
            if f'Sesión {i}' in df_marisol.columns:
                df_marisol = df_marisol[~(df_marisol[f'Link Sesión {i}'].notna() & df_marisol[f'Sesión {i}'].isna())]
        return df_marisol

    df_marisol = limpiar_conde_duque_marisol(df_marisol)

    df_golem = scrape_golem_madrid()
    df_golem['Cine'] = 'Cines Golem'

    # Cargar el CSV de Sala Equis
    try:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'salaequis.csv')
        df_salaequis = pd.read_csv(csv_path)

        # Obtener la fecha actual en el formato 'dd/mm/yyyy'
        fecha_hoy = datetime.now().strftime('%d/%m/%Y')

        # Filtrar las filas que tienen una sesión en el día de hoy
        sesion_columns = [f'Sesión {i}' for i in range(1, 6)]
        df_salaequis_hoy = df_salaequis[df_salaequis[sesion_columns].apply(lambda row: any(fecha_hoy in str(cell) for cell in row), axis=1)]

        # Añadir la columna "Cine"
        df_salaequis_hoy['Cine'] = 'Sala Equis'

    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return

    # Lista de DataFrames
    dfs = [
        df_embajadores, df_plaza_espana, df_princesa, df_retiro, 
        df_filmoteca, df_marisol, df_golem, df_cineteca, df_verdi, df_CBA, df_berlanga, df_ideal, df_salaequis_hoy  # Añadimos df_salaequis_hoy
    ]

    # Asegurar que todos los DataFrames tengan las mismas columnas
    all_columns = set()
    for df in dfs:
        all_columns.update(df.columns)

    for i in range(len(dfs)):
        df = dfs[i]
        for col in all_columns:
            if col not in df.columns:
                df[col] = pd.NA
        dfs[i] = df[sorted(all_columns)]

    # Combinar todos los DataFrames en uno solo
    all_data = pd.concat(dfs, ignore_index=True)

    # Reemplazar los valores NaN con null antes de guardar en JSON
    all_data = all_data.where(pd.notnull(all_data), None)

    # Ordenar por título antes de convertir a JSON
    all_data = all_data.sort_values(by='Título', ascending=True)

    # Guardar los datos en un archivo JSON
    peliculas_sesiones = all_data.to_dict(orient='records')

    # Ruta fija al directorio deseado
    json_path = r'C:/Users/Equipo 66/Desktop/RLCinema/rlcinema/data/cartelera.json'

    # Guardar el archivo JSON en la ruta específica
    try:
        with open(json_path, 'w') as f:
            json.dump(peliculas_sesiones, f, indent=4)
        print(f"Archivo 'cartelera.json' guardado exitosamente en {json_path}.")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

    return all_data  # Asegúrate de que esta línea esté dentro de la función


# Solo imprime el DataFrame si se ejecuta este archivo directamente
if __name__ == '__main__':
    cartelera = obtener_cartelera_combinada()
    print(cartelera)