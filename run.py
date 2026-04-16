import os
from flask import Flask, render_template, request
import telebot
import config

app = Flask(__name__, template_folder='templates')
bot = telebot.TeleBot(config.BOT_TOKEN)
ADMIN_ID = "8630490789"

# Asegurar que existe carpeta para archivos temporales
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # 1. Obtener datos del formulario
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        # 2. Obtener archivos
        portada = request.files['portada']
        video = request.files['video']
        
        if portada and video:
            # Guardar archivos localmente
            video_path = os.path.join(UPLOAD_FOLDER, video.filename)
            video.save(video_path)
            
            # Notificar al Admin
            mensaje = (
                f"🎬 <b>NUEVA PRODUCCIÓN EN COLA</b>\n"
                f"───────────────────\n"
                f"📦 <b>Obra:</b> {nombre}\n"
                f"📝 <b>Reseña:</b> {descripcion}\n"
                f"📂 <b>Archivo:</b> {video.filename}\n"
                f"───────────────────\n"
                f"⚡ <i>Iniciando procesos de Umbrae Studio...</i>"
            )
            bot.send_message(ADMIN_ID, mensaje, parse_mode="HTML")
            
            return "✅ PRODUCCIÓN INICIADA. Revisa tu Telegram.", 200
            
    except Exception as e:
        return f"❌ Error en el servidor: {str(e)}", 500

if __name__ == "__main__":
    print("🚀 [CORE] Servidor Umbrae con soporte de carga activo...")
    app.run(host="0.0.0.0", port=8000, debug=False)
