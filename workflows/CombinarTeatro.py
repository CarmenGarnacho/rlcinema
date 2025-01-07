import pandas as pd
import json
import os
from nave10teatro import scrape_nave10_teatro
from teatro_dramatico_nacional import scrape_dramatico_teatro
from teatro_abadia import scrape_teatro_abadia
from teatro_canal import scrape_teatros_canal
from teatro_fernan_gomez import scrape_teatro_fernangomez
from teatro_español import scrape_teatro_espanol_selenium

def obtener_cartelera_combinada():
    # Llama a las funciones para obtener DataFrames
    df_nave10 = scrape_nave10_teatro()
    df_nave10['Teatro'] = 'Nave10'

    df_centro = scrape_dramatico_teatro()
    df_centro['Teatro'] = 'Centro Dramático Nacional'

    df_abadia = scrape_teatro_abadia()
    df_abadia['Teatro'] = 'Teatro Abadía'

    df_canal = scrape_teatros_canal()
    df_canal['Teatro'] = 'Teatro Canal'
    
    df_fernangomez = scrape_teatro_fernangomez()
    df_fernangomez['Teatro'] = 'Teatro Fernán Gómez'

    df_spanyol = scrape_teatro_espanol_selenium()
    df_spanyol['Teatro'] = 'Teatro Español'


    # Lista de DataFrames
    dfs = [
        df_nave10, df_centro, df_abadia, df_canal, df_fernangomez, df_spanyol
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

    # Obtener la ruta del directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'cartelerateatro.json')

    # Guardar el archivo JSON en la ruta adecuada
    try:
        with open(json_path, 'w') as f:
            json.dump(peliculas_sesiones, f, indent=4)
        print("Archivo 'cartelerateatro.json' guardado exitosamente.")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

    return all_data

# Solo imprime el DataFrame si se ejecuta este archivo directamente
if __name__ == '__main__':
    cartelera = obtener_cartelera_combinada()
    print(cartelera)
