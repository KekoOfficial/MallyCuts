import os
import threading
import time
import subprocess
from flask import Flask, render_template, request, jsonify
import main

# --- MOTOR DE LIBERACIÓN DE INFRAESTRUCTURA ---
def force_kill_port(port):
    """Fuerza el cierre de cualquier proceso en el puerto usando lsof."""
    try:
        # Buscamos el PID que usa el puerto y lo matamos con SIGKILL
        pid = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
        if pid:
            os.system(f"kill -9 {pid}")
            print(f"⚡ Proceso fantasma {pid} eliminado en puerto {port}.")
    except Exception:
        pass

# --- VALIDACIÓN DE INTEGRIDAD ---
try:
    import config
except ImportError:
    print("❌ Error: No se detectó config.py.")
    exit(1)

app = Flask(__name__)

# Asegurar persistencia de directorios
for folder in [config.TEMP_FOLDER, 'static', 'templates']:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
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
        
        threading.Thread(
            target=main.motor_mallycuts_express, 
            args=(p_vid, p_port, nombre, desc),
            daemon=True
        ).start()
        
        return f"""
        <body style="background:#020202; color:#bc00ff; font-family:monospace; padding:40px; text-align:center;">
            <h1 style="letter-spacing:5px;">🚀 DESPLIEGUE INICIADO</h1>
            <hr border="1" color="#bc00ff" style="opacity:0.2;">
            <p style="color:#eee;">Procesando: <b>{nombre}</b></p>
            <br>
            <a href="/" style="color:#00f2ff; text-decoration:none; border:1px solid #00f2ff; padding:10px 20px; border-radius:10px;">[ VOLVER AL PANEL ]</a>
        </body>
        """
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Cambiamos al puerto 8081 para evitar conflictos con servicios de Android/Termux
    TARGET_PORT = 8081 
    os.system('clear')
    print("==========================================")
    print("   UMBRAE STUDIO - MALLY SERIES V3.2      ")
    print("==========================================")
    
    force_kill_port(TARGET_PORT)
    time.sleep(0.5)
    
    print(f"🛰️  Panel: http://0.0.0.0:{TARGET_PORT}")
    print(f"🎬 Engine: Umbrae Core V3.2")
    print("==========================================")
    
    app.run(host='0.0.0.0', port=TARGET_PORT, debug=False, threaded=True)
