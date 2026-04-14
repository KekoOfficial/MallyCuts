import os, time, threading, queue, subprocess
import config, logger, cortes, enviar
from tiktok_uploader.upload import upload_video # pip install tiktok-uploader

cola_produccion = queue.Queue(maxsize=2)

def trabajador_productor(p_vid, total_caps, mally_log):
    """Cerebro 1: Productor de cortes"""
    for n in range(1, total_caps + 1):
        try:
            path = cortes.extraer_segmento(p_vid, n)
            if os.path.exists(path):
                cola_produccion.put({'n': n, 'path': path, 'caption': mally_log.exito(n)})
                print(f"📦 [PROD] Cap {n} listo.")
        except Exception as e:
            print(f"❌ Error Corte Cap {n}: {e}")
    cola_produccion.put(None)

def trabajador_enviador():
    """Cerebro 2: Despacho Dual Sincronizado"""
    while True:
        p = cola_produccion.get()
        if p is None: break
        
        try:
            # --- FASE 1: TELEGRAM ---
            print(f"🚀 [TG] Enviando Cap {p['n']}...")
            enviar.despachar_a_telegram(p['path'], p['caption'])
            
            # --- PAUSA DE SEGURIDAD ---
            time.sleep(config.PAUSA_ENTRE_PLATAFORMAS)
            
            # --- FASE 2: TIKTOK ---
            print(f"📱 [TT] Publicando Cap {p['n']}...")
            upload_video(
                p['path'],
                description=f"{p['caption']} #MallySeries #Series #Viral #EscenaEn15",
                cookies=config.COOKIES_FILE,
                browser='chrome'
            )
            print(f"✅ Cap {p['n']} completado en ambos.")
        except Exception as e:
            print(f"⚠️ Error en despacho Cap {p['n']}: {e}")
        finally:
            if os.path.exists(p['path']): os.remove(p['path'])
            cola_produccion.task_done()

def motor_mallycuts_express(p_vid, p_port, nombre, desc):
    """Orquestador Imperial"""
    # 1. Análisis
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total_caps = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total_caps)

    # 2. Portada
    try:
        with open(p_port, 'rb') as img:
            enviar.bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
        os.remove(p_port)
    except: pass

    # 3. Lanzamiento Sincronizado
    tp = threading.Thread(target=trabajador_productor, args=(p_vid, total_caps, mally_log))
    te = threading.Thread(target=trabajador_enviador)

    tp.start()
    te.start()
    tp.join()
    te.join()

    # 4. Finalización
    enviar.bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")
    if os.path.exists(p_vid): os.remove(p_vid)
    print("👑 [MALLY] Misión Dual Finalizada con Éxito.")
