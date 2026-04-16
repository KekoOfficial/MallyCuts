import os
import threading
import time
from flask import Flask, render_template, request, jsonify

# --- VALIDACIÓN DE INFRAESTRUCTURA UMBRAE ---
try:
    import config
    import main
    # Verificación mecánica de credenciales
    if not hasattr(config, 'BOT_TOKEN') or not hasattr(config, 'CHAT_ID'):
        raise AttributeError
except (ImportError, AttributeError):
    print("❌ Error: Estructura de config.py inválida o incompleta.")
    print("Asegúrate de tener BOT_TOKEN y CHAT_ID definidos en config.py")
    exit(1)

app = Flask(__name__)

# Asegurar que el entorno de producción esté listo
if not os.path.exists(config.TEMP_FOLDER):
    os.makedirs(config.TEMP_FOLDER)

@app.route('/')
def index():
    """Portal de control de MallyCuts"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Recepción de archivos y disparo del motor paralelo"""
    try:
        nombre = request.form.get('nombre', 'Serie Mally')
        desc = request.form.get('descripcion', 'Sin descripción.')
        
        video = request.files.get('video')
        portada = request.files.get('portada')
        
        if not video or not portada:
            return jsonify({"status": "error", "message": "Faltan archivos esenciales."}), 400

        # Generar rutas únicas para evitar colisiones en el Xiaomi
        timestamp = int(time.time())
        p_vid = os.path.join(config.TEMP_FOLDER, f"v_{timestamp}_{video.filename}")
        p_port = os.path.join(config.TEMP_FOLDER, f"p_{timestamp}_{portada.filename}")
        
        # Guardado físico inicial
        video.save(p_vid)
        portada.save(p_port)
        
        # 🚀 LANZAMIENTO DEL MOTOR (Segundo Plano)
        # Esto permite que la web responda de inmediato mientras el bot trabaja
        threading.Thread(
            target=main.motor_mallycuts_express, 
            args=(p_vid, p_port, nombre, desc),
            daemon=True
        ).start()
        
        return f"""
        <body style="background:#000; color:#0f0; font-family:monospace; padding:20px;">
            <h1>👑 MOTOR MALLYCUTS ACTIVADO</h1>
            <hr color="#0f0">
            <p><b>Serie:</b> {nombre}</p>
            <p><b>Estado:</b> Procesando en segundo plano en Termux...</p>
            <p><i>Puedes cerrar esta pestaña, el proceso seguirá en la terminal.</i></p>
            <br>
            <a href="/" style="color:#fff;">[ Volver al Panel ]</a>
        </body>
        """

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    os.system('clear')
    print("==========================================")
    print("   UMBRAE STUDIO - MALLY SERIES V3.1      ")
    print("==========================================")
    print(f"🛰️  Servidor activo en: http://0.0.0.0:8080")
    print(f"📂 Carpeta temporal: {config.TEMP_FOLDER}")
    print(f"🎬 Duración de clips: {config.CLIP_DURATION}s")
    print("==========================================")
    
    # Ejecución en el puerto 8080 solicitado
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
