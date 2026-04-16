import os
import sys
import time
import subprocess
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import telebot
# Nuevas librerías para la lógica de cortes (antiguo cortes.py)
from moviepy.editor import VideoFileClip

# ==========================================
#   UMBRAE STUDIO - NÚCLEO SINCRONIZADO V3.1
#   (Configuración de Infraestructura Core)
# ==========================================

# Identidad del Bot y Destino Oficial (Mally Series)
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
# Canal/Grupo Mally Series (donde van las series completas)
CHAT_ID_CANAL = "-1003584710096" 

# --- CORRECCIÓN DE PRIVACIDAD: TU ID PERSONAL ---
# Pon aquí tu ID personal de Telegram (ej: "8630490789")
# Para que el Bot te notifique solo a ti en privado.
ADMIN_PERSONAL_ID = "TU_ID_PERSONAL_AQUÍ" 

# Branding Oficial & Distribución
TG_OFFICIAL = "t.me/MallySeries"
TT_OFFICIAL = "@EscenaDe15"
STUDIO_NAME = "Umbrae Studio"

# Gestión de Archivos (Rutas en Termux)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos tu carpeta temporal definida en la infraestructura
PRODUCTION_FOLDER = os.path.join(BASE_DIR, "mally_studio_segments") 
os.makedirs(PRODUCTION_FOLDER, exist_ok=True)

# Parámetros de Video (Optimización para móvil en Paraguay)
VIDEO_CODEC = "libx264"
PRESET_SPEED = "ultrafast"  # Velocidad máxima para el CPU de Termux
CRF_QUALITY = "23"          # Balance premium entre peso y nitidez
VIDEO_BITRATE = "2500k"     # Bitrate estable para subida local
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"

# --- MÓDULO: CORTES LOCAL (lógica cortes.py) ---
# Número de segmentos automáticos al subir un video (ej: 2)
# El sistema dividirá el video original en esta cantidad de partes iguales.
NUM_SEGMENTS_AUTOCUT = 2 

# Estética & Marca de Agua (lógica marcas.py)
WATERMARK_TEXT = f"TG: MallySeries | TT: EscenaDe15"
WATERMARK_COLOR = "white@0.4" # Look translúcido profesional
WATERMARK_SIZE = 28           # Tamaño balanceado para móvil
SHADOW_OPACITY = 0.6          # Sombra para lectura en escenas claras

# Inteligencia de Red y Recursos
MAX_RETRIES = 7               # Aumentado para zonas de baja señal
TIMEOUT_SEND = 600            # 10 min de espera para archivos pesados
MAX_CONCURRENT_JOBS = 1       # Protección térmica ESTRICTA para Termux (1 renderizado a la vez)
MAX_UPLOAD_SIZE_MB = 1024     # Límite de subida (1GB) para Web Local (Puerto 8080)
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
#   MÓDULO: PROCESAMIENTO DE MEDIA (lógica marcas.py + cortes.py)
# ==========================================

def procesar_video_imperial(video_path, portada_path, nombre_serie, descripcion):
    """
    HILO SEPARADO: Corta el video, aplica marca de agua, optimiza y envía a Telegram.
    Protege el procesador de Termux usando un semáforo.
    """
    with job_semaphore: # Asegura que solo corra un renderizado a la vez
        log_imperial(f"🛠️ [PROCESO MASTER] Iniciando producción maestra sincronizada de: {nombre_serie}...")
        
        try:
            # 1. --- MÓDULO CORTES: Gestión de Segmentos (lógica cortes.py) ---
            log_imperial(f"🎬 [CORTES] Analizando video original para auto-corte en {NUM_SEGMENTS_AUTOCUT} partes...")
            clip = VideoFileClip(video_path)
            duracion_total = clip.duration
            clip.close() # Cerrar clip original
            
            duracion_segmento = duracion_total / NUM_SEGMENTS_AUTOCUT
            log_imperial(f"🎬 [CORTES] Duración total: {duracion_total:.2f}s | Segmentos de {duracion_segmento:.2f}s")
            
            for chapter in range(1, NUM_SEGMENTS_AUTOCUT + 1):
                log_imperial(f"🛠️ [PROCESO {chapter}/{NUM_SEGMENTS_AUTOCUT}] Iniciando ciclo completo para Capítulo {chapter}...")
                
                # Definir tiempos de corte
                start_time = (chapter - 1) * duracion_segmento
                end_time = chapter * duracion_segmento
                
                filename = os.path.basename(video_path)
                name_part, ext = os.path.splitext(filename)
                # Nombre único para el segmento procesado
                output_filename = f"PROCESADO_{name_part}_Cap{chapter}{ext}"
                output_path = os.path.join(PRODUCTION_FOLDER, output_filename)
                
                # 2. --- MÓDULO MARCAS: FFmpeg Imperial (lógica marcas.py) ---
                # Filtro drawtext complejo para marca de agua con sombra
                filter_complex = (
                    f"drawtext=text='{WATERMARK_TEXT}':x=10:y=H-th-10:"
                    f"fontcolor={WATERMARK_COLOR}:fontsize={WATERMARK_SIZE}:"
                    f"shadowcolor=black@{SHADOW_OPACITY}:shadowx=2:shadowy=2"
                )
                
                command = [
                    'ffmpeg', '-y', # Sobrescribir si existe
                    '-ss', str(start_time), # Tiempo de inicio del corte
                    '-t', str(duracion_segmento), # Duración del corte
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
                
                log_imperial(f"🎬 [FFMPEG CAP{chapter}] Ejecutando renderizado optimizado de corte...")
                process = subprocess.Popen(command, stdout=stdout_dest, stderr=stderr_dest, text=True)
                
                if DEBUG_MODE:
                    for line in process.stderr:
                        print(f"[FFMPEG-DEBUG] {line.strip()}")
                
                process.wait() # Esperar a que FFmpeg termine el capítulo
                
                if process.returncode != 0:
                    raise Exception(f"FFmpeg falló en Capítulo {chapter} con código {process.returncode}")
                    
                log_imperial(f"✅ [FFMPEG CAP{chapter}] Capítulo renderizado con éxito: {output_filename}")
                
                # 3. --- MÓDULO DISTRIBUCIÓN: (lógica enviar.py con branding EscenaDe15) ---
                # Caption optimizado para capítulos cortos (Escena de 15)
                subida_exitosa = enviar_a_telegram_imperial(output_path, portada_path, nombre_serie, descripcion, chapter)
                
                # --- LIMPIEZA DE ARCHIVO PROCESADO ---
                if subida_exitosa:
                    try:
                        os.remove(output_path)
                        log_imperial(f"🧹 [LIMPIEZA CAP{chapter}] Segmento procesado eliminado.")
                    except OSError as e:
                        log_imperial(f"⚠️ [LIMPIEZA] Error eliminando segmento: {str(e)}")
                
                # Pausa táctica entre capítulos para no "inundar" Telegram
                log_imperial(f"⚡ [COOLDOWN] Esperando {PAUSA_ENTRE_CAPS}s antes del siguiente segmento...")
                time.sleep(PAUSA_ENTRE_CAPS)
            
            # 4. --- LIMPIEZA FINAL DE ARCHIVOS ORIGINALES ---
            log_imperial(f"🏆 [EXITO MAESTRO] Producción sincronizada de {nombre_serie} completada.")
            try:
                os.remove(video_path)
                os.remove(portada_path)
                log_imperial(f"🧹 [LIMPIEZA FINAL] Archivos originales eliminados.")
            except OSError as e:
                log_imperial(f"⚠️ [LIMPIEZA FINAL] Error eliminando originales: {str(e)}")
            
        except Exception as e:
            error_msg = f"❌ [ERROR CRÍTICO MAESTRO] Falló el ciclo sincronizado de {nombre_serie}: {str(e)}"
            log_imperial(error_msg)

# ==========================================
#   MÓDULO: TELEGRAM SEND (lógica enviar.py con reintentos)
# ==========================================

def enviar_a_telegram_imperial(video_processed_path, portada_path, nombre_serie, descripcion, chapter):
    """Envía el video procesado y la portada al canal oficial Mally Series (con branding EscenaDe15)"""
    log_imperial(f"📡 [TELEGRAM CAP{chapter}] Iniciando subida de segmento a {TG_OFFICIAL}...")
    
    # Capitalizar para el mensaje de marca
    studio_upper = STUDIO_NAME.upper()
    
    # Caption optimizado para Escena de 15 (Capítulos)
    caption_imperial = (
        f"👑 <b>{studio_upper} PRESENTA:</b>\n"
        f"───────────────────\n"
        f"🎬 <b>{nombre_serie} • Capítulo {chapter}</b>\n"
        f"📝 <b>Info:</b> {descripcion}\n"
        f"───────────────────\n"
        f"📡 <b>Oficial:</b> {TG_OFFICIAL}\n"
        f"🎥 <b>TikTok:</b> {TT_OFFICIAL}\n"
        f"⚡ <i>Umbrae Sincronizado V3.1 (AutoCortes)</i>"
    )
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Abrir archivos en modo binario para envío
            with open(video_processed_path, 'rb') as video_file, open(portada_path, 'rb') as photo_file:
                
                # Enviar video con portada (thumb) y caption HTML
                bot.send_video(
                    CHAT_ID_CANAL, 
                    video_file, 
                    caption=caption_imperial, 
                    parse_mode="HTML",
                    thumb=photo_file, # Usar la portada subida como miniatura
                    supports_streaming=True, # Permitir reproducir sin descargar completo
                    timeout=TIMEOUT_SEND # Tiempo de espera para archivos grandes
                )
                
            log_imperial(f"🏆 [EXITO TELEGRAM CAP{chapter}] Publicado oficialmente en {TG_OFFICIAL}.")
            return True # Retorna True si tiene éxito la subida
            
        except Exception as e:
            retries += 1
            log_imperial(f"⚠️ [REINTENTO CAP{chapter} {retries}/{MAX_RETRIES}] Error enviando a Telegram: {str(e)}")
            time.sleep(10) # Esperar antes de reintentar
            
    log_imperial(f"❌ [FALLO TOTAL CAP{chapter}] No se pudo enviar el segmento tras {MAX_RETRIES} intentos.")
    return False # Retorna False si falla la subida total

# ==========================================
#   MÓDULO: WEB APP LOCAL (lógica run.py - Puerto 8080)
# ==========================================

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series localmente en puerto 8080"""
    log_imperial("🌐 [WEB] Acceso local a la interfaz principal detectado.")
    try:
        return render_template('index.html')
    except Exception as e:
        log_imperial(f"❌ ERROR CARGANDO PLANTILLA index.html: {str(e)}")
        return f"❌ Error en el servidor local. Asegúrate de tener templates/index.html.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Recibe los archivos de la Web Local y lanza el hilo de procesamiento sincronizado"""
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

        # 3. LANZAR EL CICLO DE PRODUCCIÓN MAESTRO EN UN HILO SEPARADO
        # Esto permite responder "OK" a la web de inmediato, sin bloquearla
        # El hilo se encargará de: Cortar, Marcar, Enviar, Limpiar.
        processing_thread = threading.Thread(
            target=procesar_video_imperial,
            args=(video_path, portada_path, nombre_serie, descripcion)
        )
        processing_thread.start()
        
        # 4. Responder a la Web Local
        return jsonify({
            "status": "success", 
            "message": f"🔥 PRODUCCIÓN MAESTRA DE '{nombre_serie}' INICIADA (AutoCorte en {NUM_SEGMENTS_AUTOCUT} caps). Revisa {TG_OFFICIAL} en unos minutos."
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
    print(f"   {STUDIO_NAME.upper()} - CORE V3.1 (SINCRONIZADO)")
    print("     TODO EN UNO: WEB (8080) + CORTES + ENVÍOS PRIVADOS")
    print("==========================================")
    
    # --- CORRECCIÓN DE PUERTO: VOLVER AL 8080 LOCAL ---
    # Para mantener el "Ruth" o la gestión de antes que mencionas.
    log_imperial(f"🚀 Iniciando Master Core sincronizado en PUERTO 8080 LOCAL...")
    log_imperial(f"📡 Logs locales guardándose en: {LOG_FILE}")
    log_imperial(f"📡 Accede a la Web Local en http://0.0.0.0:8080")
    log_imperial(f"📡 AutoCortes de Mally Series configurado en: {NUM_SEGMENTS_AUTOCUT} capítulos.")
    log_imperial(f"⚠️ NOTA LOCAL PARAGUAY: Funcionando sin túnel HTTPS. Usar WiFi local para subir media.")
    
    # --- CORRECCIÓN DE PRIVACIDAD: NOTIFICACIÓN PRIVADA AL ADMIN ---
    if ADMIN_PERSONAL_ID != "TU_ID_PERSONAL_AQUÍ":
        try:
            bot.send_message(ADMIN_PERSONAL_ID, f"🛡️ <b>Core {STUDIO_NAME} Sincronizado V3.1 LOCAL (Puerto 8080)</b>\nSistemas de AutoCorte operativos. Solo tú has sido notificado, Noa.", parse_mode="HTML")
            log_imperial(f"📡 Notificación de arranque enviada PRIVADAMENTE al ID {ADMIN_PERSONAL_ID}.")
        except Exception as e:
            log_imperial(f"⚠️ No se pudo enviar notificación PRIVADA a Telegram. Verifica tu ID: {str(e)}")
    else:
        log_imperial(f"⚠️ Configura ADMIN_PERSONAL_ID en main.py para recibir notificaciones privadas de arranque.")

    try:
        # IMPORTANTE PARA TERMUX LOCAL: host 0.0.0.0, Puerto 8080, use_reloader=False
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        log_imperial(f"\n🛑 Apagando sistemas imperiales de {STUDIO_NAME} por solicitud del usuario...")
        sys.exit(0)
