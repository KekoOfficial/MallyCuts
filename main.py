import os
import sys
import time
import subprocess
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import telebot

# ==========================================
#   UMBRAE STUDIO - NÚCLEO SINCRONIZADO V3.0
#   (Configuración de Infraestructura Core)
# ==========================================

# Identidad del Bot y Destino Oficial (Mally Series)
# Sustituye con tu token real
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
# Asegúrate de que el bot sea ADMIN en este canal
CHAT_ID = "-1003584710096" 

# Branding Oficial & Distribución
TG_OFFICIAL = "t.me/MallySeries"
TT_OFFICIAL = "@EscenaDe15"
STUDIO_NAME = "Umbrae Studio"

# Gestión de Archivos (Rutas en Termux)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos tu carpeta temporal definida en la infraestructura
PRODUCTION_FOLDER = os.path.join(BASE_DIR, "mally_studio_segments") 
os.makedirs(PRODUCTION_FOLDER, exist_ok=True)

# Renderizado de Video (Optimización para móvil en Paraguay)
VIDEO_CODEC = "libx264"
PRESET_SPEED = "ultrafast"  # Velocidad máxima para el CPU de Termux
CRF_QUALITY = "23"          # Balance premium entre peso y nitidez
VIDEO_BITRATE = "2500k"     # Bitrate estable para subida local
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"

# Estética & Marca de Agua (Branding Style)
WATERMARK_TEXT = f"TG: MallySeries | TT: EscenaDe15"
WATERMARK_COLOR = "white@0.4" # Look translúcido profesional
WATERMARK_SIZE = 28           # Tamaño balanceado para móvil
SHADOW_OPACITY = 0.6          # Sombra para lectura en escenas claras

# Inteligencia de Red y Recursos
MAX_RETRIES = 7               # Aumentado para zonas de baja señal
TIMEOUT_SEND = 600            # 10 min de espera para archivos pesados
MAX_CONCURRENT_JOBS = 1       # Protección térmica ESTRICTA para Termux (1 renderizado a la vez)
MAX_UPLOAD_SIZE_MB = 500      # Límite de subida para la Web Local
PAUSA_ENTRE_CAPS = 3          # Evita FloodWait de Telegram (lógica cortes.py)

# Logging y Debug (lógica logger.py)
LOG_FILE = os.path.join(BASE_DIR, "umbras_studio_core.log")
DEBUG_MODE = False            # Cambiar a True para ver errores de FFmpeg

# ==========================================
#   INICIALIZACIÓN DE SISTEMAS CENTRALES
# ==========================================

app = Flask(__name__, template_folder='templates')
bot = telebot.TeleBot(BOT_TOKEN)

# Limitar tamaño de subida en la Web Local (Flask)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Semáforo para controlar trabajos concurrentes (Protección Térmica Termux)
job_semaphore = threading.Semaphore(MAX_CONCURRENT_JOBS)

# ==========================================
#   MÓDULO: LOGGER IMPERIAL (lógica logger.py)
# ==========================================

def log_imperial(mensaje):
    """Función de logging centralizada"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 👑 {STUDIO_NAME} {mensaje}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

# ==========================================
#   MÓDULO: PROCESAMIENTO DE MEDIA (FFmpeg + lógica marcas.py + cortes.py)
# ==========================================

def procesar_video_imperial(video_path, portada_path, nombre_serie, descripcion):
    """
    HILO SEPARADO: Aplica marca de agua, optimiza y envía a Telegram.
    Protege el procesador de Termux usando un semáforo.
    """
    with job_semaphore: # Asegura que solo corra un renderizado a la vez
        log_imperial(f"🛠️ [PROCESO] Iniciando producción maestra de: {nombre_serie}...")
        
        filename = os.path.basename(video_path)
        # Nombres de archivo limpios y seguros (secure_filename ya aplicado en /upload)
        output_filename = f"PROCESADO_{filename}"
        output_path = os.path.join(PRODUCTION_FOLDER, output_filename)
        
        # --- COMANDO FFMPEG IMPERIAL (Marca de Agua + Optimización) ---
        # Filtrodrawtext complejo para marca de agua con sombra
        filter_complex = (
            f"drawtext=text='{WATERMARK_TEXT}':x=10:y=H-th-10:"
            f"fontcolor={WATERMARK_COLOR}:fontsize={WATERMARK_SIZE}:"
            f"shadowcolor=black@{SHADOW_OPACITY}:shadowx=2:shadowy=2"
        )
        
        command = [
            'ffmpeg', '-y', # Sobrescribir si existe
            '-i', video_path,
            '-vf', filter_complex, # Aplicar filtro de branding
            '-c:v', VIDEO_CODEC,
            '-preset', PRESET_SPEED,
            '-crf', CRF_QUALITY,
            '-b:v', VIDEO_BITRATE,
            '-c:a', AUDIO_CODEC,
            '-b:a', AUDIO_BITRATE,
            output_path
        ]
        
        # Redirigir logs según DEBUG_MODE
        stdout_dest = subprocess.PIPE if DEBUG_MODE else subprocess.DEVNULL
        stderr_dest = subprocess.PIPE if DEBUG_MODE else subprocess.DEVNULL
        
        try:
            log_imperial(f"🎬 [FFMPEG] Ejecutando renderizado de {nombre_serie} optimizado para móvil...")
            process = subprocess.Popen(command, stdout=stdout_dest, stderr=stderr_dest, text=True)
            
            if DEBUG_MODE:
                # Si está en debug, imprimir la salida de FFmpeg
                for line in process.stderr:
                    print(f"[FFMPEG-DEBUG] {line.strip()}")
            
            process.wait() # Esperar a que FFmpeg termine
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg falló con código {process.returncode}")
                
            log_imperial(f"✅ [FFMPEG] Renderizado imperial completado: {output_filename}")
            
            # Pausa táctica entre capítulos para no "inundar" Telegram
            time.sleep(PAUSA_ENTRE_CAPS)
            
            # --- MÓDULO: DISTRIBUCIÓN (enviar_a_telegram, lógica enviar.py) ---
            subida_exitosa = enviar_a_telegram_imperial(output_path, portada_path, nombre_serie, descripcion)
            
            # --- LIMPIEZA DE ARCHIVOS TEMPORALES ---
            if subida_exitosa:
                try:
                    os.remove(video_path)
                    os.remove(portada_path)
                    os.remove(output_path)
                    log_imperial(f"🧹 [LIMPIEZA] Archivos temporales de {nombre_serie} eliminados.")
                except OSError as e:
                    log_imperial(f"⚠️ [LIMPIEZA] Error eliminando temporales: {str(e)}")
            else:
                 log_imperial(f"🛑 [LIMPIEZA] No se borraron los archivos debido a fallo en la subida.")
            
        except Exception as e:
            error_msg = f"❌ [ERROR CRÍTICO] Falló el ciclo de producción de {nombre_serie}: {str(e)}"
            log_imperial(error_msg)

# ==========================================
#   MÓDULO: TELEGRAM SEND (lógica enviar.py con reintentos)
# ==========================================

def enviar_a_telegram_imperial(video_processed_path, portada_path, nombre_serie, descripcion):
    """Envía el video procesado y la portada al canal oficial Mally Series"""
    log_imperial(f"📡 [TELEGRAM] Iniciando subida de {nombre_serie} a {TG_OFFICIAL}...")
    
    # Capitalizar para el mensaje de marca
    studio_upper = STUDIO_NAME.upper()
    
    caption_imperial = (
        f"👑 <b>{studio_upper} PRESENTA:</b>\n"
        f"───────────────────\n"
        f"🎬 <b>{nombre_serie}</b>\n"
        f"📝 <b>Reseña:</b> {descripcion}\n"
        f"───────────────────\n"
        f"📡 <b>Oficial:</b> {TG_OFFICIAL}\n"
        f"🎥 <b>TikTok:</b> {TT_OFFICIAL}\n"
        f"⚡ <i>Powered by Umbrae Sincronizado V3.0</i>"
    )
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Abrir archivos en modo binario para envío
            with open(video_processed_path, 'rb') as video_file, open(portada_path, 'rb') as photo_file:
                
                # Enviar video con portada (thumb) y caption HTML
                bot.send_video(
                    CHAT_ID, 
                    video_file, 
                    caption=caption_imperial, 
                    parse_mode="HTML",
                    thumb=photo_file, # Usar la portada subida como miniatura
                    supports_streaming=True, # Permitir reproducir sin descargar completo
                    timeout=TIMEOUT_SEND # Tiempo de espera para archivos grandes
                )
                
            log_imperial(f"🏆 [EXITO] {nombre_serie} publicada oficialmente en {TG_OFFICIAL}.")
            return True # Retorna True si tiene éxito la subida
            
        except Exception as e:
            retries += 1
            log_imperial(f"⚠️ [REINTENTO {retries}/{MAX_RETRIES}] Error enviando a Telegram: {str(e)}")
            time.sleep(10) # Esperar antes de reintentar
            
    log_imperial(f"❌ [FALLO TOTAL] No se pudo enviar {nombre_serie} tras {MAX_RETRIES} intentos.")
    return False # Retorna False si falla la subida total

# ==========================================
#   MÓDULO: WEB APP LOCAL (lógica run.py)
# ==========================================

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series localmente"""
    log_imperial("🌐 [WEB] Acceso local a la interfaz principal detectado.")
    try:
        return render_template('index.html')
    except Exception as e:
        log_imperial(f"❌ ERROR CARGANDO PLANTILLA index.html: {str(e)}")
        return f"❌ Error en el servidor local. Asegúrate de tener templates/index.html.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recibe los archivos de la Web Local y lanza el hilo de procesamiento"""
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

        # 3. LANZAR EL CICLO DE PRODUCCIÓN EN UN HILO SEPARADO
        # Esto permite responder "OK" a la web de inmediato, sin bloquearla
        processing_thread = threading.Thread(
            target=procesar_video_imperial,
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
        return jsonify({"status": "error", "message": f"Hubo un fallo en la matriz central de Umbrae: {str(e)}"}), 500

# ==========================================
#   LANZAMIENTO DEL NÚCLEO IMPERIAL (MAIN)
# ==========================================

if __name__ == "__main__":
    # Limpiar pantalla para un arranque imperial impecable
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("==========================================")
    print(f"   {STUDIO_NAME.upper()} - CORE V3.0 (SINCRONIZADO)")
    print("     TODO EN UNO: WEB + MARCAS + ENVÍOS")
    print("==========================================")
    
    log_imperial(f"🚀 Iniciando Master Core sincronizado en puerto 8000...")
    log_imperial(f"📡 Logs locales guardándose en: {LOG_FILE}")
    log_imperial(f"📡 Accede a la Web Local en http://0.0.0.0:8000")
    log_imperial(f"⚠️ NOTA LOCAL: Funcionando sin túnel HTTPS. BotFather no integrará este link.")
    
    # Notificación silenciosa de arranque al Canal Oficial
    try:
        bot.send_message(CHAT_ID, f"🛡️ <b>Core {STUDIO_NAME} Sincronizado V3.0</b>\nTodo en Uno en línea. Esperando transmisiones locales para Mally Series.", parse_mode="HTML")
    except Exception as e:
        log_imperial(f"⚠️ No se pudo enviar notificación de arranque a Telegram: {str(e)}")

    try:
        # IMPORTANTE PARA TERMUX LOCAL: host 0.0.0.0 y use_reloader=False
        # No usamos debug=True para evitar inestabilidad en producción local
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        log_imperial(f"\n🛑 Apagando sistemas imperiales de {STUDIO_NAME} por solicitud del usuario...")
        sys.exit(0)
