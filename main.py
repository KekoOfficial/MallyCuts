import os, time, threading, subprocess
from flask import Flask, render_template, request
import config, logger, cortes, editar, enviar

app = Flask(__name__)

def motor_imperial_4k(p_vid, p_port, nombre, desc):
    if not os.path.exists(config.TEMP_FOLDER): 
        os.makedirs(config.TEMP_FOLDER)
    
    # Obtener duración total
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total)

    # 1. Enviar Portada (Prioridad de Marca)
    with open(p_port, 'rb') as img:
        enviar.bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
    os.remove(p_port)

    # 2. Bucle de Producción Sincronizada
    for n in range(1, total + 1):
        print(mally_log.cortando(n))
        
        # Flujo: Cortar -> Editar (4K+Audio) -> Enviar
        raw = cortes.extraer_segmento(p_vid, n)
        final = editar.procesar_clip(raw, n)
        
        # Enviar y esperar confirmación (Garantiza el orden 1, 2, 3...)
        enviar.despachar_a_telegram(final, mally_log.exito(n))
        
        # Limpieza de archivo crudo
        if os.path.exists(raw): os.remove(raw)
        
        # Pequeño respiro para el procesador del Xiaomi
        time.sleep(1)

    # 3. Finalización
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
    
    threading.Thread(target=motor_imperial_4k, args=(p_vid, p_port, n, d)).start()
    return "<h1>🚀 PRODUCCIÓN 4K INICIADA</h1><p>Los clips llegarán en orden a @MallySeries</p>"

if __name__ == "__main__":
    # Puerto 8080 para Termux/Local
    app.run(host='0.0.0.0', port=8080)
