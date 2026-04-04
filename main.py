import os
import subprocess
import threading
from flask import Flask, render_template_string
from telebot import TeleBot
import config

# --- INICIALIZACIÓN ---
bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# --- LÓGICA DE VIDEO (MOTOR ULTRA-RÁPIDO) ---
def procesar_y_enviar(video_path, chat_id):
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)

    # 1. Aviso de inicio
    bot.send_message(chat_id, f"🚀 **Chrome Magic Good**: Iniciando segmentación de {config.CLIP_DURATION}s...")

    # 2. Comando FFmpeg (Corte sin renderizar = Velocidad de Rayo)
    output_pattern = os.path.join(config.TEMP_FOLDER, "clip_%03d.mp4")
    comando = [
        'ffmpeg', '-i', video_path,
        '-f', 'segment',
        '-segment_time', str(config.CLIP_DURATION),
        '-reset_timestamps', '1',
        '-c', 'copy', 
        output_pattern
    ]

    try:
        subprocess.run(comando, check=True, capture_output=True)
        
        # 3. Envío de clips y limpieza automática
        segmentos = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.endswith('.mp4')])
        
        for index, seg in enumerate(segmentos):
            path_seg = os.path.join(config.TEMP_FOLDER, seg)
            bot.send_message(chat_id, f"📦 **Enviando parte {index + 1}**...")
            
            with open(path_seg, 'rb') as v:
                bot.send_video(chat_id, v)
            
            os.remove(path_seg) # Borra para no llenar memoria

        bot.send_message(chat_id, "✅ **Motor Detenido**: Proceso completado con éxito.")
    
    except Exception as e:
        bot.send_message(chat_id, f"❌ **Error Crítico**: {str(e)}")

# --- MANEJADOR DE TELEGRAM ---
@bot.message_handler(content_types=['video'])
def handle_incoming_video(message):
    bot.reply_to(message, "📥 **Video Recibido**. Descargando al motor principal...")
    
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    input_tmp = "input_temp.mp4"
    with open(input_tmp, 'wb') as f:
        f.write(downloaded_file)
    
    # Procesar en un hilo separado para no bloquear el bot
    threading.Thread(target=procesar_y_enviar, args=(input_tmp, message.chat.id)).start()

# --- CONSOLA WEB (Para Chrome) ---
@app.route('/')
def index():
    # Estética Cyber-Imperial integrada directamente
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <style>
            body { background: #000; color: #00ff41; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .box { border: 2px solid #00ff41; padding: 30px; box-shadow: 0 0 20px #00ff41; background: rgba(0,255,65,0.1); border-radius: 10px; text-align: center; }
            h1 { text-shadow: 0 0 10px #00ff41; margin-bottom: 5px; }
            .status { color: #ff00ff; font-weight: bold; }
            .blink { animation: blinker 1.5s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }
        </style>
        <title>Chrome Magic Good Console</title>
    </head>
    <body>
        <div class="box">
            <h1>[ CHROME MAGIC GOOD V2 ]</h1>
            <p>> Estatus: <span class="status blink">EJECUTANDO MOTOR</span></p>
            <p>> Escaneando Puerto: 8080</p>
            <p>> Modo: Hyper-Velocity Automatizado</p>
            <hr style="border: 0.5px solid #00ff41;">
            <p style="font-size: 0.8rem;">Desarrollado por Noa | Sistema Operativo MP</p>
        </div>
    </body>
    </html>
    ''')

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# --- INICIO GLOBAL ---
if __name__ == "__main__":
    print("💎 Chrome Magic Good V2 Iniciando...")
    # Inicia la web en un hilo aparte
    threading.Thread(target=run_flask).start()
    # Inicia el Bot
    bot.polling(none_stop=True)
