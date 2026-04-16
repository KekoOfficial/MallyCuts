import os
import threading
import time
from flask import Flask, render_template, request, jsonify
import main

app = Flask(__name__)

# Asegurar infraestructura
for folder in ['static', 'templates', 'mally_studio_segments']:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        nombre = request.form.get('nombre', 'Mally Project')
        desc = request.form.get('descripcion', '')
        video = request.files.get('video')
        portada = request.files.get('portada')
        
        if not video or not portada:
            return jsonify({"status": "error", "message": "Faltan archivos"}), 400

        timestamp = int(time.time())
        p_vid = os.path.join('mally_studio_segments', f"v_{timestamp}_{video.filename}")
        p_port = os.path.join('mally_studio_segments', f"p_{timestamp}_{portada.filename}")
        
        video.save(p_vid)
        portada.save(p_port)
        
        threading.Thread(
            target=main.motor_mallycuts_express, 
            args=(p_vid, p_port, nombre, desc),
            daemon=True
        ).start()
        
        return "🚀 DESPLIEGUE EN CURSO... MIRA LA TERMINAL"
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    PORT = 9090 
    os.system('clear')
    print("==========================================")
    print("   UMBRAE STUDIO - MALLY SERIES V3.3      ")
    print("   PORT: 9090 | STATUS: ONLINE            ")
    print("==========================================")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
