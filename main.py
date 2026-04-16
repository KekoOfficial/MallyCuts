import os, subprocess, queue, threading
import config, cortes, enviar, logger

# Cola sincronizada para ligereza del procesador
cola_trabajo = queue.Queue(maxsize=config.MAX_CONCURRENT_JOBS)

def productor_de_cortes(video_path, total_caps, mally_log):
    for n in range(1, total_caps + 1):
        path = cortes.procesar_segmento(video_path, n)
        if path:
            cola_trabajo.put({'n': n, 'path': path, 'caption': mally_log.exito(n)})
            print(f"📦 Cap {n} procesado y en fila.")
    cola_trabajo.put(None) # Fin de producción

def consumidor_de_envios():
    while True:
        item = cola_trabajo.get()
        if item is None: break
        
        print(f"🚀 Enviando Cap {item['n']}...")
        if enviar.despachar_a_telegram(item['path'], item['caption']):
            print(f"✅ Cap {item['n']} enviado con éxito.")
            if os.path.exists(item['path']):
                os.remove(item['path'])
        
        time.sleep(config.PAUSA_ENTRE_CAPS)
        cola_trabajo.task_done()

def motor_mally_v3(video_path, nombre_serie):
    # Detección automática de duración
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path], capture_output=True, text=True)
    total_caps = int(float(res.stdout) // config.CLIP_DURATION) + 1
    
    mally_log = logger.MallyLogger(nombre_serie, total_caps)
    
    # Hilos en paralelo para máximo rendimiento
    hilo_corte = threading.Thread(target=productor_de_cortes, args=(video_path, total_caps, mally_log))
    hilo_envio = threading.Thread(target=consumidor_de_envios)
    
    hilo_corte.start()
    hilo_envio.start()
    
    hilo_corte.join()
    hilo_envio.join()
    
    print(f"👑 Misión Finalizada: {nombre_serie}")
