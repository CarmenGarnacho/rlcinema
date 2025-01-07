from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Cargar el archivo JSON de cine
    with open('cartelera.json', 'r', encoding='utf-8') as f:
        peliculas_sesiones = json.load(f)
    
    # Cargar el archivo JSON de teatro
    with open('cartelerateatro.json', 'r', encoding='utf-8') as f:
        obras_sesiones = json.load(f)
    
    # Cargar el archivo JSON de exposiciones
    with open('exposiciones.json', 'r', encoding='utf-8') as f:
        exposiciones_sesiones = json.load(f)
    
    # Pasar todos los conjuntos de datos a la plantilla HTML
    return render_template('index.html', 
                           peliculas_sesiones=peliculas_sesiones, 
                           obras_sesiones=obras_sesiones,
                           exposiciones_sesiones=exposiciones_sesiones)

if __name__ == '__main__':
    app.run(debug=True)
