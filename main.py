import os, time, threading, subprocess, queue
from flask import Flask, render_template, request
import config, logger, cortes, editar, enviar

app = Flask(__name__)

# Bandeja de salida para sincronizar hilos (Productor -> Enviador)
# maxsize=3 para no saturar el almacenamiento del Xiaomi mientras se sube
cola_produccion = queue.Queue(maxsize=3)

def trabajador_productor(p_vid, nombre, desc, total, mally_log):
    """
    Cerebro 1: Se encarga de la CPU (Cortar y Editar).
    No espera a que el video se suba para empezar el siguiente.
    """
    try:
        for n in range(1, total + 1):
            print(f"🛠️ [PRODUCCIÓN] Iniciando Capítulo {n}/{total}...")
            
            # 1. Cortar el segmento crudo
            raw = cortes.extraer_segmento(p_vid, n)
            
            # 2. Aplicar Filtros (4K, TikTok Style, Audio Pro)
            # Este es el paso que más consume CPU
            final = editar.procesar_clip(raw, n)
            
            # Limpiar el temporal crudo
            if os.path.exists(raw): os.remove(raw)
            
            # 3. Poner en cola para envío
            # Si la cola tiene 3 videos, este hilo espera automáticamente
            cola_produccion.put({
                'n': n,
                'path': final,
                'caption': mally_log.exito(n)
            })
            print(f"✅ [PRODUCCIÓN] Capítulo {n} listo y en espera de subida.")
            
    except Exception as e:
        print(f"❌ ERROR EN CADENA DE PRODUCCIÓN: {e}")
    finally:
        # Enviar señal de finalización al hilo de envío
        cola_produccion.put(None)

def trabajador_enviador():
    """
    Cerebro 2: Se encarga de la RED (Subida a Telegram).
    Solo se activa cuando hay algo listo en la cola_produccion.
    """
    while True:
        paquete = cola_produccion.get()
        if paquete is None: # Señal de fin
            break
        
        n = paquete['n']
        path_final = paquete['path']
        caption = paquete['caption']
        
        print(f"🚀 [SUBIDA] Despachando Capítulo {n} a @MallySeries...")
        
        try:
            # Subir a Telegram
            enviar.despachar_a_telegram(path_final, caption)
            print(f"🏁 [SUBIDA] Capítulo {n} enviado con éxito.")
        except Exception as e:
            print(f"⚠️ Error al subir capítulo {n}: {e}")
        finally:
            # Limpiar el archivo procesado después de subirlo
            if os.path.exists(path_final):
                os.remove(path_final)
            cola_produccion.task_done()

def motor_mallycuts_v2(p_vid, p_port, nombre, desc):
    """Orquestador Principal del Imperio"""
    if not os.path.exists(config.TEMP_FOLDER): 
        os.makedirs(config.TEMP_FOLDER)

    # Obtener duración y calcular total de capítulos
    res = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', p_vid
    ], capture_output=True, text=True)
    
    duracion_total = float(res.stdout)
    total_caps = int(duracion_total // config.CLIP_DURATION) + (1 if duracion_total % config.CLIP_DURATION > 0 else 0)
    
    mally_log = logger.MallyLogger(nombre, total_caps)

    # 1. Enviar Portada (Sincrónico para abrir el hilo en Telegram)
    try:
        with open(p_port, 'rb') as img:
            enviar.bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
        os.remove(p_port)
    except Exception as e:
        print(f"❌ Error al enviar portada: {e}")

    # 2. Iniciar Motores en Paralelo
    hilo_prod = threading.Thread(target=trabajador_productor, args=(p_vid, nombre, desc, total_caps, mally_log))
    hilo_env = threading.Thread(target=trabajador_enviador)

    hilo_prod.start()
    hilo_env.start()

    # Esperar a que ambos terminen su trabajo
    hilo_prod.join()
    hilo_env.join()

    # 3. Mensaje Final de Misión Cumplida
    enviar.bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")
    if os.path.exists(p_vid): os.remove(p_vid)
    print("👑 [SISTEMA] Serie completa procesada y enviada.")

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    n = request.form.get('nombre', 'Serie Sin Nombre')
    d = request.form.get('descripcion', '')
    
    p_vid = f"v_{int(time.time())}.mp4"
    p_port = f"p_{int(time.time())}.jpg"
    
    request.files['video'].save(p_vid)
    request.files['portada'].save(p_port)
    
    # Lanzar el motor en un hilo aparte para no bloquear la web
    threading.Thread(target=motor_mallycuts_v2, args=(p_vid, p_port, n, d)).start()
    
    return "<h1>🚀 MOTOR MALLYCUTS V2 INICIADO</h1><p>Procesando en modo multi-hilo para máxima velocidad.</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
