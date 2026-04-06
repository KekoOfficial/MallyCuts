import os
import subprocess
import threading
import time
from flask import Flask, render_template_string, request
from telebot import TeleBot, apihelper
import config
import logger

# --- CONFIGURACIÓN DE RED CRÍTICA PARA TERMUX ---
# Aumentamos el tiempo de espera a 10 minutos por cada subida
apihelper.CONNECT_TIMEOUT = 600 
apihelper.READ_TIMEOUT = 600
bot = TeleBot(config.API_TOKEN, threaded=False)

app = Flask(__name__)

def enviar_inmediato(path_v, n, total, mally_log):
    """Procesa la miniatura y envía el capítulo de forma asíncrona"""
    path_t = path_v.replace(".mp4", ".jpg")
    
    # Generar miniatura del segundo 02 para evitar cuadros negros
    subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:02', '-vframes', '1', path_t], capture_output=True)
    
    # Obtener el caption avanzado desde el logger
    caption = mally_log.exito(n)
    
    for intento in range(3):
        try:
            with open(path_v, 'rb') as v, open(path_t, 'rb') as t:
                bot.send_video(
                    config.CHAT_ID, 
                    v, 
                    thumb=t, 
                    caption=caption, 
                    parse_mode="HTML", 
                    timeout=600
                )
            print(f"🎉 Capítulo {n} subido con éxito.")
            break 
        except Exception as e:
            print(f"⚠️ Reintento {intento+1} para capítulo {n}: {e}")
            time.sleep(10)
    
    # Limpieza inmediata para ahorrar espacio en Termux
    if os.path.exists(path_v): os.remove(path_v)
    if os.path.exists(path_t): os.remove(path_t)

def motor_mally_pro(path_video, original_name):
    """Motor principal: Corta 1 -> Envía 1 -> Corta el siguiente"""
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # 1. Obtener duración y calcular capítulos de 3 min
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path_video], capture_output=True, text=True)
    total_capitulos = int(float(res.stdout) // config.CLIP_DURATION) + 1
    
    # Instanciar el logger avanzado
    mally_log = logger.MallyLogger(original_name, total_capitulos)
    
    # 2. Aviso de Inicio en el canal
    bot.send_message(config.CHAT_ID, mally_log.inicio(), parse_mode="HTML")

    # 3. Bucle de Corte y Envío Secuencial
    for i in range(total_capitulos):
        n = i + 1
        inicio_seg = i * config.CLIP_DURATION
        salida_clip = os.path.join(config.TEMP_FOLDER, f"capitulo_{n:03d}.mp4")
        
        # Cortar segmento actual (Copia directa para máxima velocidad)
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(inicio_seg), '-t', str(config.CLIP_DURATION),
            '-i', path_video, '-c', 'copy', '-avoid_negative_ts', '1', salida_clip
        ], check=True)
        
        print(mally_log.cortando(n))
        
        # ENVIAR AHORA (No espera al siguiente corte)
        enviar_inmediato(salida_clip, n, total_capitulos, mally_log)
        time.sleep(2) # Respiro para el procesador

    # 4. Aviso final y limpieza del video original
    if os.path.exists(path_video): os.remove(path_video)
    bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")

# --- INTERFAZ WEB (SELECCIÓN DESDE GALERÍA) ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MALLY SERIES STUDIO</title>
        <style>
            body { background:#000; color:#0f0; font-family:monospace; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
            .box { border: 2px solid #0f0; padding: 40px; background:rgba(0,20,0,0.9); border-radius:15px; text-align:center; box-shadow: 0 0 20px #0f0; }
            h1 { color:#f0f; text-shadow: 2px 2px #000; margin-bottom: 20px; }
            .btn { display:inline-block; padding:20px 40px; background:#f0f; color:#fff; font-weight:bold; cursor:pointer; border-radius:10px; border:none; text-transform:uppercase; font-size: 1.1rem; }
            .btn:hover { background: #d0d; box-shadow: 0 0 15px #f0f; }
            input[type="file"] { display:none; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>MALLY SERIES STUDIO</h1>
            <p>> MODO: SELECCIÓN GALERÍA (3 MIN)</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label class="btn">
                    SELECCIONAR DE GALERÍA
                    <input type="file" name="file" accept="video/*" onchange="this.form.submit()">
                </label>
            </form>
            <p style="margin-top:20px; font-size:0.8rem; color:#888;">Asíncrono v12 | @MallySeries</p>
        </div>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file: return "Error", 400
    temp_path = f"video_{int(time.time())}.mp4"
    file.save(temp_path)
    # Iniciar motor en hilo separado para no bloquear la web
    threading.Thread(target=motor_mally_pro, args=(temp_path, file.filename)).start()
    return "<h1>🕹️ Iniciando Producción y Envío...</h1><script>setTimeout(()=>window.location='/', 2500)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
