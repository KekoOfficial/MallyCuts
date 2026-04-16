import os
import threading
import time
import signal
import sys
from flask import Flask, render_template, request, jsonify
import main

# --- AUTO-LIMPIEZA DE PUERTOS ---
def kill_port(port):
    """Mata cualquier proceso que esté bloqueando el puerto antes de iniciar."""
    try:
        # Comando para Termux/Linux que identifica y mata el proceso en el puerto
        os.system(f"fuser -k {port}/tcp > /dev/null 2>&1")
    except:
        pass

# --- VALIDACIÓN DE INFRAESTRUCTURA ---
try:
    import config
    if not hasattr(config, 'BOT_TOKEN') or not hasattr(config, 'CHAT_ID'):
        raise AttributeError
except (ImportError, AttributeError):
    print("❌ Error: Estructura de config.py inválida.")
    exit(1)

app = Flask(__name__)

# Asegurar directorios esenciales
for folder in [config.TEMP_FOLDER, 'static', 'templates']:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/')
def index():
    """Portal MallyCuts V3.1"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Motor de procesamiento en segundo plano"""
    try:
        nombre = request.form.get('nombre', 'Mally Project')
        desc = request.form.get('descripcion', 'Sin descripción.')
        video = request.files.get('video')
        portada = request.files.get('portada')
        
        if not video or not portada:
            return jsonify({"status": "error", "message": "Faltan archivos."}), 400

        timestamp = int(time.time())
        p_vid = os.path.join(config.TEMP_FOLDER, f"v_{timestamp}_{video.filename}")
        p_port = os.path.join(config.TEMP_FOLDER, f"p_{timestamp}_{portada.filename}")
        
        video.save(p_vid)
        portada.save(p_port)
        
        # Lanzamiento del motor imperial
        threading.Thread(
            target=main.motor_mallycuts_express, 
            args=(p_vid, p_port, nombre, desc),
            daemon=True
        ).start()
        
        return f"""
        <body style="background:#050505; color:#bc00ff; font-family:monospace; padding:40px; text-align:center;">
            <h1 style="letter-spacing:5px;">🚀 DESPLIEGUE INICIADO</h1>
            <hr border="1" color="#bc00ff" style="opacity:0.3;">
            <p style="color:#eee;">El proyecto <b>{nombre}</b> está siendo procesado.</p>
            <p style="color:#555;">Checkea la terminal de Termux para ver el progreso.</p>
            <br>
            <a href="/" style="color:#00f2ff; text-decoration:none; border:1px solid #00f2ff; padding:10px 20px; border-radius:10px;">[ VOLVER AL PANEL ]</a>
        </body>
        """
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    PORT = 8080
    os.system('clear')
    print("==========================================")
    print("   UMBRAE STUDIO - MALLY SERIES V3.1      ")
    print("==========================================")
    
    # Limpiamos el puerto antes de arrancar
    print(f"📡 Liberando puerto {PORT}...")
    kill_port(PORT)
    time.sleep(1) # Breve pausa para asegurar la liberación
    
    print(f"🛰️  Servidor activo en: http://0.0.0.0:{PORT}")
    print(f"📂 Carpeta temporal: {config.TEMP_FOLDER}")
    print(f"🖼️  Logo detectado: /static/logo_umbrae.png")
    print("==========================================")
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
