import os, time, threading, queue, subprocess
import config, logger, cortes, enviar

# Buffer optimizado para archivos crudos
cola_produccion = queue.Queue(maxsize=5)

def trabajador_productor(p_vid, total, mally_log):
    """Cerebro 1: Corte Directo Sincronizado"""
    for n in range(1, total + 1):
        try:
            print(f"✂️ [CORTE] Extrayendo Capítulo {n}/{total}...")
            
            # El video sale directo de cortes.py
            path_segmento = cortes.extraer_segmento(p_vid, n)
            
            if os.path.exists(path_segmento) and os.path.getsize(path_segmento) > 1000:
                # Sincronizamos directamente con la cola de envío
                cola_produccion.put({
                    'n': n, 
                    'path': path_segmento, 
                    'caption': mally_log.exito(n)
                })
                print(f"✅ [CORTE] Capítulo {n} listo para despacho.")
            else:
                print(f"⚠️ [CORTE] Error de integridad en Cap {n}.")
                
        except Exception as e:
            print(f"❌ [CORTE] Fallo crítico en Cap {n}: {e}")
    
    cola_produccion.put(None) # Fin de producción

def trabajador_enviador():
    """Cerebro 2: Despacho de Red Sincronizado"""
    while True:
        paquete = cola_produccion.get()
        if paquete is None: break
        
        try:
            print(f"🚀 [RED] Subiendo Cap {paquete['n']}...")
            # Enviamos el archivo original sin editar
            exito = enviar.despachar_a_telegram(paquete['path'], paquete['caption'])
            
            if exito:
                print(f"🏁 [RED] Cap {paquete['n']} enviado.")
        finally:
            if os.path.exists(paquete['path']):
                os.remove(paquete['path'])
            cola_produccion.task_done()

def motor_mallycuts_express(p_vid, p_port, nombre, desc):
    """Orquestador Sincronizado Sin Edición"""
    # ... (Cálculo de duración y envío de portada igual)
    
    hilo_p = threading.Thread(target=trabajador_productor, args=(p_vid, total_caps, mally_log))
    hilo_e = threading.Thread(target=trabajador_enviador)

    hilo_p.start()
    hilo_e.start()

    hilo_p.join()
    hilo_e.join()

    enviar.bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")
    print("👑 [SISTEMA] Misión Express Finalizada.")
