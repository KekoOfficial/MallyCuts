import os, threading, queue, subprocess
import config, logger, cortes, enviar

cola_produccion = queue.Queue(maxsize=5)

def trabajador_productor(p_vid, total, mally_log):
    for n in range(1, total + 1):
        try:
            path = cortes.extraer_segmento(p_vid, n, aplicar_marca=False)
            cola_produccion.put({'n': n, 'path': path, 'caption': mally_log.exito(n)})
        except Exception as e: print(f"❌ Error Cap {n}: {e}")
    cola_produccion.put(None)

def trabajador_enviador():
    while True:
        p = cola_produccion.get()
        if p is None: break
        try:
            enviar.despachar_a_telegram(p['path'], p['caption'])
        finally:
            if os.path.exists(p['path']): os.remove(p['path'])
            cola_produccion.task_done()

def motor_mallycuts_express(p_vid, p_port, nombre, desc):
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total_caps = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total_caps)

    with open(p_port, 'rb') as img:
        enviar.bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
    os.remove(p_port)

    tp = threading.Thread(target=trabajador_productor, args=(p_vid, total_caps, mally_log))
    te = threading.Thread(target=trabajador_enviador)
    tp.start(); te.start(); tp.join(); te.join()

    enviar.bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")
    if os.path.exists(p_vid): os.remove(p_vid)
