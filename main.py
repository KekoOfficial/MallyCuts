import os, subprocess, threading, time
from flask import Flask, render_template, request
from telebot import TeleBot, apihelper
import config, logger

# Optimización de red para archivos editados (pueden pesar más)
apihelper.CONNECT_TIMEOUT = 800
bot = TeleBot(config.API_TOKEN, threaded=False)
app = Flask(__name__)

def enviar_asincrono(path_v, n, total, mally_log):
    path_t = path_v.replace(".mp4", ".jpg")
    # Miniatura rápida del segundo 2
    subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:02', '-vframes', '1', path_t], capture_output=True)
    
    for _ in range(3): # Reintentos en caso de lag en Termux
        try:
            with open(path_v, 'rb') as v, open(path_t, 'rb') as t:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=mally_log.exito(n), parse_mode="HTML", timeout=800)
            break
        except: time.sleep(10)
    
    # Limpieza inmediata de clips enviados
    if os.path.exists(path_v): os.remove(path_v)
    if os.path.exists(path_t): os.remove(path_t)

def motor_mally_pro(p_vid, p_port, nombre, desc):
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # Obtener info del video original
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total)

    # 1. ENVIAR PORTADA E INFORMACIÓN
    try:
        with open(p_port, 'rb') as img:
            bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
        os.remove(p_port)
    except Exception as e: print(f"Error Portada: {e}")

    # 2. ETAPA DE EDICIÓN: Aplicar Marca de Agua (Video Maestro)
    p_vid_editado = p_vid.replace(".mp4", "_mally.mp4")
    print(f"⚙️ Iniciando edición de marca de agua...")
    
    # Comando para incrustar texto abajo a la derecha
    # Usamos fuentes del sistema Android/Termux
    cmd_edit = [
        'ffmpeg', '-y', '-i', p_vid,
        '-vf', f"drawtext=text='{config.WATERMARK_TEXT}':x=w-tw-20:y=h-th-20:fontcolor={config.WATERMARK_COLOR}:fontsize=28",
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23', # Codificación rápida
        '-c:a', 'copy', p_vid_editado
    ]
    
    subprocess.run(cmd_edit, check=True)

    # 3. BUCLE DE CORTES ASÍNCRONOS
    for i in range(total):
        n = i + 1
        salida = os.path.join(config.TEMP_FOLDER, f"clip_{n:03d}.mp4")
        
        # Cortar del video ya editado con marca de agua
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(i*config.CLIP_DURATION), '-t', str(config.CLIP_DURATION),
            '-i', p_vid_editado, '-c', 'copy', '-avoid_negative_ts', '1', salida
        ], check=True)
        
        print(f"⚙️ {mally_log.cortando(n)}")
        
        # Envío inmediato
        enviar_asincrono(salida, n, total, mally_log)

    # Limpieza final de archivos maestros
    if os.path.exists(p_vid): os.remove(p_vid)
    if os.path.exists(p_vid_editado): os.remove(p_vid_editado)
    bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    n, d = request.form['nombre'], request.form['descripcion']
    p_port, p_vid = f"port_{time.time()}.jpg", f"orig_{time.time()}.mp4"
    request.files['portada'].save(p_port)
    request.files['video'].save(p_vid)
    
    threading.Thread(target=motor_mally_pro, args=(p_vid, p_port, n, d)).start()
    return "<h1>🕹️ PRODUCCIÓN INICIADA</h1><script>setTimeout(()=>window.location='/', 3000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
