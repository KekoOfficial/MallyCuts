import os
import sys
import time
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import telebot

# ==========================================
#   SERVER.PY - MOTOR LOCAL PURO (PUERTO 8080)
#   (Configuración de Gestión Local de Antes)
# ==========================================

# Identidad del Bot y Destino (Mally Series)
# Sustituye con tu token real
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
# Asegúrate de que el bot sea ADMIN en este canal
CHAT_ID_CANAL = "-1003584710096" 

# --- CORRECCIÓN DE PRIVACIDAD: TU ID PERSONAL ---
# Pon aquí tu ID personal de Telegram (ej: "8630490789")
# Para que el Bot te notifique solo a ti en privado.
ADMIN_PERSONAL_ID = "TU_ID_PERSONAL_AQUÍ" 

# Branding Oficial & Distribución
TG_OFFICIAL = "t.me/MallySeries"
STUDIO_NAME = "Umbrae Studio"

# Gestión de Archivos (Rutas en Termux)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos tu carpeta temporal definida en la infraestructura
PRODUCTION_FOLDER = os.path.join(BASE_DIR, "mally_studio_segments") 
os.makedirs(PRODUCTION_FOLDER, exist_ok=True)

# Recursos y Seguridad
MAX_UPLOAD_SIZE_MB = 1024     # Límite de subida (1GB) para Web Local (Puerto 8080)
MAX_CONCURRENT_JOBS = 1       # Protección térmica ESTRICTA para Termux

# Logging y Debug (lógica logger.py)
LOG_FILE = os.path.join(BASE_DIR, "umbras_studio_core.log")

# ==========================================
#   INICIALIZACIÓN DE SISTEMAS CENTRALES
# ==========================================

app = Flask(__name__, template_folder='templates')
bot = telebot.TeleBot(BOT_TOKEN)

# Limitar tamaño de subida en la Web Local (Flask)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Semáforo para controlar trabajos concurrentes y proteger Termux
job_semaphore = threading.Semaphore(MAX_CONCURRENT_JOBS)

# ==========================================
#   MÓDULO: LOGGER IMPERIAL (lógica logger.py)
# ==========================================

def log_imperial(mensaje):
    """Función de logging centralizada"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 🌐 {STUDIO_NAME} {mensaje}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

# ==========================================
#   MÓDULO: LLAMADA AL CEREBRO (main.py)
# ==========================================

def llamar_al_cerebro_sincronizado(video_path, portada_path, nombre_serie, descripcion):
    """
    HILO SEPARADO: Llama a la función de procesamiento en main.py.
    Protege el procesador de Termux usando un semáforo.
    """
    with job_semaphore: # Asegura que solo corra un renderizado a la vez
        log_imperial(f"🛠️ [PROCESO] Iniciando ciclo maestro para: {nombre_serie}...")
        
        try:
            # --- FUSIÓN MAESTRA: IMPORTACIÓN DE MAIN.PY ---
            # Asumimos que main.py tiene una función llamada 'procesar_video_imperial'
            # y que está en el mismo directorio.
            import main as cerebro
            
            # Lanza el procesamiento completo: Cortar, Marcar, Enviar, Limpiar
            cerebro.procesar_video_imperial(video_path, portada_path, nombre_serie, descripcion)
            
            log_imperial(f"🏆 [EXITO] Producción sincronizada de {nombre_serie} completada.")
            
        except ImportError:
            log_imperial(f"❌ ERROR CRÍTICO: No se pudo importar main.py. Verifica que esté en el mismo directorio.")
        except AttributeError:
            log_imperial(f"❌ ERROR CRÍTICO: main.py no tiene la función 'procesar_video_imperial'.")
        except Exception as e:
            error_msg = f"❌ [ERROR MAESTRO] Falló el ciclo sincronizado de {nombre_serie}: {str(e)}"
            log_imperial(error_msg)

# ==========================================
#   RUTAS DE LA WEB LOCAL (FLASK - Puerto 8080)
# ==========================================

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series localmente en puerto 8080"""
    log_imperial("🌐 [WEB] Acceso local a la interfaz principal de Ruth detectado.")
    try:
        return render_template('index.html')
    except Exception as e:
        log_imperial(f"❌ ERROR CARGANDO PLANTILLA index.html: {str(e)}")
        return f"❌ Error en el servidor local. Asegúrate de tener templates/index.html.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recibe los archivos de la Web Local y llama al Hilo Sincronizado"""
    log_imperial("🔄 [WEB] Intento de subida local para Mally Series recibido...")
    
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
        # Limpiamos los nombres de archivo antes de guardarlos
        v_filename = secure_filename(video.filename)
        p_filename = secure_filename(portada.filename)
        
        # Asegurar nombres únicos para evitar colisiones
        timestamp = int(time.time())
        v_filename = f"{timestamp}_{v_filename}"
        p_filename = f"{timestamp}_{p_filename}"
        
        video_path = os.path.join(PRODUCTION_FOLDER, v_filename)
        portada_path = os.path.join(PRODUCTION_FOLDER, p_filename)
        
        video.save(video_path)
        portada.save(portada_path)
        
        log_imperial(f"📥 [WEB] Archivos recibidos y guardados localmente: {v_filename}")

        # 3. LANZAR EL HILO DE LLAMADA AL CEREBRO EN SEGUNDO PLANO
        # Esto permite responder "OK" a la web de inmediato, sin bloquearla
        processing_thread = threading.Thread(
            target=llamar_al_cerebro_sincronizado,
            args=(video_path, portada_path, nombre_serie, descripcion)
        )
        processing_thread.start()
        
        # 4. Responder a la Web Local
        return jsonify({
            "status": "success", 
            "message": f"🔥 PRODUCCIÓN DE '{nombre_serie}' INICIADA. Revisa {TG_OFFICIAL} en unos minutos."
        }), 200

    except Exception as e:
        log_imperial(f"❌ ERROR CRÍTICO EN /UPLOAD: {str(e)}")
        return jsonify({"status": "error", "message": f"Hubo un fallo en la matriz local de Umbrae: {str(e)}"}), 500

# ==========================================
#   LANZAMIENTO DEL MOTOR LOCAL (MAIN)
# ==========================================

if __name__ == "__main__":
    # Limpiar pantalla para un arranque imperial impecable
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("==========================================")
    print(f"   {STUDIO_NAME.upper()} - MOTOR LOCAL PURO (PUERTO 8080)")
    print("     TODO EN UNO: WEB + LLAMADA AL CEREBRO")
    print("==========================================")
    
    log_imperial(f"🚀 Iniciando Motor Local sincronizado en PUERTO 8080 LOCAL...")
    log_imperial(f"📡 Logs locales guardándose en: {LOG_FILE}")
    log_imperial(f"📡 Accede a la Web Local en http://0.0.0.0:8080")
    log_imperial(f"⚠️ NOTA LOCAL PARAGUAY: Funcionando sin túnel HTTPS. Usar WiFi local para subir media.")
    
    # --- CORRECCIÓN DE PRIVACIDAD: NOTIFICACIÓN PRIVADA AL ADMIN ---
    if ADMIN_PERSONAL_ID != "TU_ID_PERSONAL_AQUÍ":
        try:
            bot.send_message(ADMIN_PERSONAL_ID, f"🛡️ <b>Ruth Umbrae LOCAL Sincronizado V3.1 (Puerto 8080)</b>\nListo para recibir Mally Series. Solo tú has sido notificado, Noa.", parse_mode="HTML")
            log_imperial(f"📡 Notificación de arranque enviada PRIVADAMENTE al ID {ADMIN_PERSONAL_ID}.")
        except Exception as e:
            log_imperial(f"⚠️ No se pudo enviar notificación PRIVADA a Telegram. Verifica tu ID: {str(e)}")
    else:
        log_imperial(f"⚠️ Configura ADMIN_PERSONAL_ID en server.py para recibir notificaciones privadas de arranque.")

    try:
        # IMPORTANTE PARA TERMUX LOCAL: host 0.0.0.0, Puerto 8080, use_reloader=False
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        log_imperial(f"\n🛑 Apagando sistemas locales de {STUDIO_NAME} por solicitud del usuario...")
        sys.exit(0)
