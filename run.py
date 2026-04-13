import os
from flask import Flask, render_template, request
import threading
import main  # Importamos el motor lógico
import config

app = Flask(__name__)

# Asegurar que la carpeta temporal existe al iniciar
if not os.path.exists(config.TEMP_FOLDER):
    os.makedirs(config.TEMP_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    nombre = request.form.get('nombre', 'Serie Mally')
    desc = request.form.get('descripcion', '')
    
    # Guardar archivos con nombres únicos para evitar choques
    import time
    timestamp = int(time.time())
    p_vid = f"video_{timestamp}.mp4"
    p_port = f"portada_{timestamp}.jpg"
    
    request.files['video'].save(p_vid)
    request.files['portada'].save(p_port)
    
    # LANZAMIENTO SINCRONIZADO: Corremos el motor en un hilo
    # para que la web no se quede "cargando" y el proceso siga en el terminal
    threading.Thread(
        target=main.motor_mallycuts_express, 
        args=(p_vid, p_port, nombre, desc)
    ).start()
    
    return f"<h1>🚀 MOTOR MALLYCUTS INICIADO</h1><p>Serie: {nombre}<br>Procesando en segundo plano...</p>"

if __name__ == "__main__":
    print("""
    👑 MALLY SERIES - SISTEMA OPTIMIZADO
    ------------------------------------
    Iniciando servidor en: http://0.0.0.0:8080
    Modo: Sincronizado Express (Corte Directo)
    """)
    app.run(host='0.0.0.0', port=8080, debug=False)
