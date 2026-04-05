# 1. IMPORTACIÓN E INFRAESTRUCTURA
import os, subprocess, threading, time
from contextlib import ExitStack
from flask import Flask, render_template_string, request
from telebot import TeleBot, apihelper
import config

# Configuración de Red
apihelper.READ_TIMEOUT = config.READ_TIMEOUT
apihelper.CONNECT_TIMEOUT = config.CONNECT_TIMEOUT
bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# 2. FUNCIÓN DE ENVÍO (EL "MENSAJERO")
def despachador_de_clips(nombre_serie, total_esperado):
    """Revisa la carpeta y envía los clips que FFmpeg va soltando."""
    enviados = 0
    proceso_activo = True
    
    bot.send_message(config.CHAT_ID, f"🎬 <b>PRODUCCIÓN EN VIVO</b>\n<b>Serie:</b> {nombre_serie}", parse_mode="HTML")

    while enviados < total_esperado:
        # Listar archivos actuales que ya estén terminados
        todos_los_archivos = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_') and f.endswith('.mp4')])
        
        # Solo intentamos enviar si hay al menos un archivo "adelantado" 
        # (para asegurar que FFmpeg ya terminó de escribirlo)
        if len(todos_los_archivos) > 1 or (enviados == total_esperado - 1 and len(todos_los_archivos) == 1):
            clip_name = todos_los_archivos[0]
            path_v = os.path.join(config.TEMP_FOLDER, clip_name)
            path_t = path_v.replace(".mp4", ".jpg")
            enviados += 1

            # Generar miniatura
            subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)
            caption = f"🎬 <b>{nombre_serie}</b>\n💎 <b>Parte:</b> {enviados}\n✅ @MallySeries"

            # Intento de envío con reintentos
            for intento in range(1, config.MAX_RETRIES + 1):
                try:
                    with ExitStack() as stack:
                        v = stack.enter_context(open(path_v, 'rb'))
                        t = stack.enter_context(open(path_t, 'rb')) if os.path.exists(path_t) else None
                        bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML", timeout=config.READ_TIMEOUT)
                    print(f"✔️ {clip_name} enviado.")
                    break
                except Exception as e:
                    print(f"⚠️ Reintento {intento} para {clip_name}: {e}")
                    time.sleep(10)

            # Limpiar
            if os.path.exists(path_v): os.remove(path_v)
            if os.path.exists(path_t): os.remove(path_t)
            time.sleep(2) # Respiro para el sistema
        else:
            # Si FFmpeg aún no suelta el siguiente, esperamos 3 segundos
            time.sleep(3)

    bot.send_message(config.CHAT_ID, f"🏁 <b>TEMPORADA FINALIZADA</b>", parse_mode="HTML")

# 3. MOTOR PRINCIPAL (EL "CORTADOR")
def motor_mally_pro(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    # Calcular cuántos clips saldrán aproximadamente (Duración / CLIP_DURATION)
    # Esto es para que el despachador sepa cuándo terminar
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path])
    total_segundos = float(probe)
    total_esperado = int(total_segundos // config.CLIP_DURATION) + (1 if total_segundos % config.CLIP_DURATION > 0 else 0)

    # Iniciar el hilo de ENVÍO antes de empezar a cortar
    hilo_envio = threading.Thread(target=despachador_de_clips, args=(original_name, total_esperado))
    hilo_envio.start()

    # Iniciar el proceso de CORTE (FFmpeg)
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, 
            '-f', 'segment', '-segment_time', str(config.CLIP_DURATION),
            '-reset_timestamps', '1', '-c', 'copy', output_pattern
        ], check=True)
    except Exception as e:
        print(f"❌ Error en corte: {e}")

    hilo_envio.join() # Esperar a que termine de enviar el último
    if os.path.exists(video_path): os.remove(video_path)

# 4. INTERFAZ WEB
@app.route('/')
def index():
    return render_template_string('''<body style="background:#000;color:#e50914;text-align:center;padding-top:100px;font-family:sans-serif;"><h1>MALLY <span style="color:#fff">LIVE-PRO</span></h1><form action="/upload" method="post" enctype="multipart/form-data"><label style="background:#e50914;color:#fff;padding:15px 30px;cursor:pointer;font-weight:bold;">NUEVA PRODUCCIÓN EN VIVO<input type="file" name="file" accept="video/*" onchange="this.form.submit()" style="display:none;"></label></form></body>''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = "input_pro.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_pro, args=(save_path, file.filename)).start()
    return "<h1>🚀 Producción en tiempo real iniciada...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
