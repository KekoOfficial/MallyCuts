import os, time, threading, subprocess
from flask import Flask, render_template, request
import config, logger, cortes, marcas, enviar

app = Flask(__name__)

def motor_imperial_cascada(p_vid, p_port, nombre, desc):
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # 1. Obtener total de clips
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total)

    # 2. Enviar Portada (Prioridad de entrada)
    with open(p_port, 'rb') as img:
        enviar.bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
    os.remove(p_port)

    # 3. Ciclo de Producción Cascada
    for n in range(1, total + 1):
        print(f"⚙️ {mally_log.cortando(n)}")
        
        # Flujo: Cortar -> Editar -> Enviar
        tmp_raw = cortes.extraer_segmento(p_vid, n)
        tmp_final = marcas.aplicar_marca_agua(tmp_raw, n)
        
        enviar.despachar_a_telegram(tmp_final, mally_log.exito(n))
        
        # Eliminar el raw sobrante
        if os.path.exists(tmp_raw): os.remove(tmp_raw)
        
        # Breve pausa anti-spam para Telegram
        time.sleep(1.5)

    # Finalización
    if os.path.exists(p_vid): os.remove(p_vid)
    enviar.bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")

@app.route('/')
def index(): return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    n, d = request.form['nombre'], request.form['descripcion']
    p_vid, p_port = f"v_{time.time()}.mp4", f"p_{time.time()}.jpg"
    request.files['video'].save(p_vid)
    request.files['portada'].save(p_port)
    
    threading.Thread(target=motor_imperial_cascada, args=(p_vid, p_port, n, d)).start()
    return "<h1>🚀 Producción en Cascada Activa</h1><p>Los clips llegarán ordenados a @MallySeries</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
