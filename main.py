import os
import sys
import time
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import telebot

# --- IMPORTACIÓN DE MÓDULOS DEL IMPERIO IMP ---
# Aquí conectamos main.py con toda tu infraestructura sincronizada
try:
    import config as cfg # Carga la configuración core unificada
    import logger # Sistema de registro y notificaciones privadas
    import cortes # Lógica de auto-cortes y gestión de media
    # enviar y marcas se cargan dentro de cortes para mayor sincronización
    
    # Notificación de arranque PRIVADA (Solo para Noa)
    bot = telebot.TeleBot(cfg.BOT_TOKEN)
    if cfg.ADMIN_PERSONAL_ID != "TU_ID_PERSONAL_AQUÍ":
        bot.send_message(cfg.ADMIN_PERSONAL_ID, f"🛡️ <b>Core {cfg.STUDIO_NAME} Sincronizado V3.1 LOCAL (Puerto 8000)</b>\nListo para recibir Mally Series.\n\nHe activado los sistemas delegados (Cortes, Marcas, Envíos).\n\nSolo tú has sido notificado, Noa.", parse_mode="HTML")
        logger.registrar_log(f"📡 Notificación de arranque enviada PRIVADAMENTE al ID {cfg.ADMIN_PERSONAL_ID}.")
    else:
        logger.registrar_log(f"⚠️ Configura ADMIN_PERSONAL_ID en config.py para recibir notificaciones privadas de arranque.")

except ImportError as e:
    print(f"❌ Error Crítico de Fusión: No se pudo importar un módulo vital: {str(e)}")
    print("Asegúrate de que config.py, logger.py, cortes.py, marcas.py y enviar.py estén en el mismo directorio.")
    sys.exit(1)
except Exception as e:
    logger.registrar_log(f"⚠️ No se pudo enviar notificación PRIVADA a Telegram. Verifica tu ID: {str(e)}")


# ==========================================
#   INICIALIZACIÓN DEL SISTEMA WEB (Flask)
# ==========================================

app = Flask(__name__, template_folder='templates')

# Limitar tamaño de subida en la Web Local (Flask)
app.config['MAX_CONTENT_LENGTH'] = cfg.MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Semáforo para controlar trabajos concurrentes (Protección Térmica)
# Delegamos el control de jobs a cortes.py para mayor sincronización
job_semaphore = threading.Semaphore(cfg.MAX_CONCURRENT_JOBS)

# ==========================================
#   RUTAS DE LA WEB LOCAL (FLASK - Puerto 8000)
# ==========================================

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series localmente en puerto 8000"""
    logger.registrar_log("🌐 [WEB] Acceso local a la interfaz principal detectado.")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.registrar_log(f"❌ ERROR CARGANDO PLANTILLA index.html: {str(e)}")
        return f"❌ Error en el servidor local. Asegúrate de tener templates/index.html.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recibe los archivos de la Web Local y orquesta el ciclo en segundo plano"""
    logger.registrar_log("🔄 [WEB] Intento de subida local para Mally Series recibido...")
    
    try:
        # 1. Validación estricta de campos del formulario HTML
        nombre_serie = request.form.get('nombre', 'Mally Serie Sin Título')
        descripcion = request.form.get('descripcion', 'Sin reseña oficial')
        
        if 'portada' not in request.files or 'video' not in request.files:
            return jsonify({"status": "error", "message": "⚠️ Faltan archivos en el formulario."}), 400
            
        portada = request.files['portada']
        video = request.files['video']
        
        if video.filename == '' or portada.filename == '':
             return jsonify({"status": "error", "message": "⚠️ Debes seleccionar video y portada."}), 400

        # 2. Guardado Seguro de archivos (secure_filename + Timestamp)
        v_filename = secure_filename(video.filename)
        p_filename = secure_filename(portada.filename)
        
        # Asegurar nombres únicos para evitar colisiones
        timestamp = int(time.time())
        v_filename = f"{timestamp}_{v_filename}"
        p_filename = f"{timestamp}_{p_filename}"
        
        # Guardamos en la carpeta de producción unificada localmente
        video_path = os.path.join(cfg.PRODUCTION_FOLDER, v_filename)
        portada_path = os.path.join(cfg.PRODUCTION_FOLDER, p_filename)
        
        video.save(video_path)
        portada.save(portada_path)
        
        logger.registrar_log(f"📥 [WEB] Archivos recibidos y guardados localmente: {v_filename}")

        # 3. LANZAR EL CICLO DE PRODUCCIÓN MAESTRO EN UN HILO SEPARADO
        # DELEGAMOS LA ORQUESTACIÓN A cortes.py
        processing_thread = threading.Thread(
            target=cortes.orquestar_produccion_sincronizada,
            args=(video_path, portada_path, nombre_serie, descripcion, job_semaphore)
        )
        processing_thread.start()
        
        # 4. Responder a la Web Local
        return jsonify({
            "status": "success", 
            "message": f"🔥 PRODUCCIÓN DE '{nombre_serie}' INICIADA. Revisa Mally Series en unos minutos."
        }), 200

    except Exception as e:
        logger.registrar_log(f"❌ ERROR CRÍTICO EN /UPLOAD: {str(e)}")
        return jsonify({"status": "error", "message": f"Hubo un fallo en la matriz central de Umbrae: {str(e)}"}), 500

# ==========================================
#   LANZAMIENTO DEL NÚCLEO LOCAL (MAIN)
# ==========================================

if __name__ == "__main__":
    # Limpiar pantalla para un arranque imperial blindado localmente
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("==========================================")
    print(f"   {cfg.STUDIO_NAME.upper()} - CORE V3.1 (SINCRONIZADO)")
    print("     TODO EN UNO: WEB (8000) + CORTES DELEGADOS")
    print("==========================================")
    
    logger.registrar_log(f"🚀 Iniciando Core sincronizado en PUERTO 8000 LOCAL...")
    print(f"📡 Accede a la Web Local en http://0.0.0.0:8000")
    print(f"📡 AutoCortes de Mally Series configurado en: {cfg.NUM_SEGMENTS_AUTOCUT} capítulos.")
    print(f"⚠️ NOTA LOCAL PARAGUAY: Funcionando sin túnel HTTPS. Usar WiFi local para subir media.")
    
    try:
        # IMPORTANTE PARA TERMUX LOCAL: host 0.0.0.0, Puerto 8000, use_reloader=False
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        logger.registrar_log(f"\n🛑 Apagando sistemas imperiales por solicitud del usuario...")
        sys.exit(0)
