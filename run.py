import os
import sys
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import telebot

# --- IMPORTA AQUÍ TU INFRAESTRUCTURA DE UMBRAE ---
try:
    # Asumimos que tu archivo de configuración se llama 'config_umbrae.py'
    # o 'core_infrastructure.py'. Cámbialo si es necesario.
    import config_umbrae as cfg 
    print("✅ [CORE] Infraestructura de Umbrae Studio cargada correctamente.")
except ImportError:
    print("❌ Error: No se encontró el archivo de configuración de infraestructura.")
    print("Asegúrate de que tu archivo con BOT_TOKEN y CHAT_ID esté en el mismo directorio.")
    sys.exit(1)

# --- CONFIGURACIÓN DE NÚCLEO (Importado de tu Infraestructura) ---
app = Flask(__name__, template_folder='templates')
bot = telebot.TeleBot(cfg.BOT_TOKEN)
CANAL_ID = cfg.CHAT_ID # Usamos tu CHAT_ID para el canal oficial

# Directorio de trabajo seguro para Termux y Mally Series
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Usamos tu carpeta temporal definida en la infraestructura
UPLOAD_FOLDER = os.path.join(BASE_DIR, cfg.TEMP_FOLDER) 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Limitar tamaño de subida (500MB) para Termux
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"❌ ERROR CARGANDO PLANTILLA: {str(e)}")
        return f"❌ Error en el servidor. Revisa los logs de Termux.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Procesa la subida de series y notifica al Canal Oficial"""
    print("🔄 [CORE] Intento de subida para Mally Series detectado...")
    try:
        # Validación de campos del formulario
        nombre = request.form.get('nombre', 'Mally Serie Sin Título')
        descripcion = request.form.get('descripcion', 'Sin reseña oficial')
        
        if 'portada' not in request.files or 'video' not in request.files:
            return "⚠️ Error: Faltan archivos en el formulario.", 400
            
        portada = request.files['portada']
        video = request.files['video']
        
        if video.filename == '':
            return "⚠️ Error: No seleccionaste ningún video para la serie.", 400
        if portada.filename == '':
             return "⚠️ Error: No seleccionaste ninguna portada.", 400

        # Guardado Seguro (Secure Filename)
        v_filename = secure_filename(video.filename)
        p_filename = secure_filename(portada.filename)
        
        video_path = os.path.join(UPLOAD_FOLDER, v_filename)
        portada_path = os.path.join(UPLOAD_FOLDER, p_filename)
        
        video.save(video_path)
        portada.save(portada_path)
        
        print(f"✅ Recibido en {cfg.STUDIO_NAME}: {v_filename} | Iniciando protocolos...")

        # Notificación Imperial al Canal Oficial (Mally Series)
        # Usamos tu branding definido en la infraestructura
        mensaje = (
            f"👑 <b>{cfg.STUDIO_NAME} • PRODUCCIÓN RECOLECTADA</b>\n"
            f"───────────────────\n"
            f"🎬 <b>Serie:</b> {nombre}\n"
            f"📝 <b>Reseña:</b> {descripcion}\n"
            f"📦 <b>Video:</b> {v_filename}\n"
            f"🖼️ <b>Portada:</b> {p_filename}\n"
            f"───────────────────\n"
            f"⚡ <i>Sincronizando con {cfg.TG_OFFICIAL} v2.0...</i>"
        )
        
        # Envía mensaje al canal oficial
        try:
            bot.send_message(CANAL_ID, mensaje, parse_mode="HTML")
            print(f"📡 Notificación enviada al canal {cfg.TG_OFFICIAL}")
        except Exception as e:
            print(f"❌ Error enviando mensaje a Telegram Canal: {str(e)}")
            # El archivo está guardado, la notificación es secundaria.

        return f"🔥 PRODUCCIÓN INICIADA. El Staff de {cfg.STUDIO_NAME} ha sido notificado.", 200

    except Exception as e:
        # Imprime el error real en la consola de Termux
        print(f"❌ ERROR CRÍTICO EN UPLOAD: {str(e)}")
        return f"Hubo un fallo en la matriz central de Umbrae: {str(e)}", 500

# --- LANZAMIENTO DEL SERVIDOR ---
if __name__ == "__main__":
    print("------------------------------------------")
    print(f"   {cfg.STUDIO_NAME.upper()} - CORE V2.1")
    print("     INTEGRACIÓN CON INFRAESTRUCTURA ACTIVA")
    print("------------------------------------------")
    print("🚀 Servidor Flask en línea en el puerto 8000")
    print(f"📡 Asegúrate de tener cloudflared corriendo en otra pestaña para HTTPS.")
    
    try:
        # Notificación silenciosa de arranque al Canal Oficial
        try:
            bot.send_message(CANAL_ID, f"🛡️ <b>Core {cfg.STUDIO_NAME} Sincronizado</b>\nListo para recibir Mally Series.", parse_mode="HTML")
        except Exception:
            pass # Ignorar si falla la notificación inicial

        # IMPORTANTE: host 0.0.0.0 y use_reloader=False para Termux
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print(f"\n🛑 Apagando sistemas de {cfg.STUDIO_NAME} por solicitud del usuario...")
        sys.exit(0)
