import os
import sys
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import telebot
import config

# --- CONFIGURACIÓN DE NÚCLEO ---
app = Flask(__name__, template_folder='templates')
bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = "8630490789"

# Directorio de trabajo seguro para Termux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Limitar tamaño de subida (ejemplo 500MB) para evitar cuelgues
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 

@app.route('/')
def index():
    """Carga la interfaz principal de Mally Series"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"❌ Error: No se encontró index.html en /templates. ({str(e)})"

@app.route('/upload', methods=['POST'])
def upload_file():
    """Procesa la subida de series y notifica al Staff"""
    try:
        # Validación de campos
        nombre = request.form.get('nombre', 'Proyecto Sin Nombre')
        descripcion = request.form.get('descripcion', 'Sin reseña')
        
        if 'portada' not in request.files or 'video' not in request.files:
            return "⚠️ Error: Faltan archivos en el formulario.", 400
            
        portada = request.files['portada']
        video = request.files['video']
        
        if video.filename == '':
            return "⚠️ Error: No seleccionaste ningún video.", 400

        # Guardado Seguro
        v_filename = secure_filename(video.filename)
        p_filename = secure_filename(portada.filename)
        
        video_path = os.path.join(UPLOAD_FOLDER, v_filename)
        portada_path = os.path.join(UPLOAD_FOLDER, p_filename)
        
        video.save(video_path)
        portada.save(portada_path)
        
        print(f"✅ Recibido: {v_filename} | Iniciando protocolos...")

        # Notificación Imperial a Telegram
        mensaje = (
            f"👑 <b>UMBRAE STUDIO • PRODUCCIÓN</b>\n"
            f"───────────────────\n"
            f"🎬 <b>Obra:</b> {nombre}\n"
            f"📝 <b>Reseña:</b> {descripcion}\n"
            f"📦 <b>Video:</b> {v_filename}\n"
            f"🖼️ <b>Portada:</b> {p_filename}\n"
            f"───────────────────\n"
            f"⚡ <i>Sincronizando con Mally Series...</i>"
        )
        
        bot.send_message(ADMIN_ID, mensaje, parse_mode="HTML")
        
        return "🔥 PRODUCCIÓN INICIADA. El Staff ha sido notificado.", 200

    except Exception as e:
        print(f"❌ ERROR EN SISTEMA: {str(e)}")
        return f"Hubo un fallo en la matriz: {str(e)}", 500

# --- LANZAMIENTO ---
if __name__ == "__main__":
    print("------------------------------------------")
    print("   UMBRAE STUDIO CORE V2 - BY NOA         ")
    print("------------------------------------------")
    print("🚀 Servidor en línea en el puerto 8000")
    print(f"📡 Local: http://localhost:8000")
    
    try:
        # Notificación silenciosa de arranque
        bot.send_message(ADMIN_ID, "🛡️ <b>Core Umbrae Sincronizado</b>\nListo para recibir contenido.", parse_mode="HTML")
        
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Apagando sistemas imperiales...")
        sys.exit()
