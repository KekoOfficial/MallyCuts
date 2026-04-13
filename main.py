import os
import time
import threading
import queue
import subprocess
import config
import logger
import cortes
import enviar

# --- CONFIGURACIÓN DE SINCRONÍA ---
# Buffer de 5 videos para asegurar que el Enviador siempre tenga trabajo
cola_produccion = queue.Queue(maxsize=5)

def trabajador_productor(p_vid, total_caps, mally_log):
    """
    Cerebro 1: Producción Directa.
    Extrae segmentos sin re-codificar para máxima velocidad.
    """
    print(f"⚙️ [SISTEMA] Productor iniciado. Rango: 1-{total_caps}")
    
    for n in range(1, total_caps + 1):
        try:
            # 1. Corte Sincronizado (Casi instantáneo con '-c copy')
            path_segmento = cortes.extraer_segmento(p_vid, n)
            
            # 2. Verificación de Integridad
            if os.path.exists(path_segmento) and os.path.getsize(path_segmento) > 1000:
                # 3. Entrega al Buffer
                # Si la cola está llena, el Productor espera aquí (Auto-Regulación)
                cola_produccion.put({
                    'n': n,
                    'path': path_segmento,
                    'caption': mally_log.exito(n)
                })
                print(f"📦 [PROD] Cap {n} entregado a la cola de envío.")
            else:
                print(f"⚠️ [PROD] Cap {n} parece estar vacío o corrupto.")
                
        except Exception as e:
            print(f"❌ [PROD] Error crítico procesando Cap {n}: {e}")
    
    # Señal de "Fin de Producción" para el Enviador
    cola_produccion.put(None)
    print("✅ [PROD] Cadena de producción finalizada.")

def trabajador_enviador():
    """
    Cerebro 2: Despacho de Red.
    Se encarga exclusivamente de la comunicación con los servidores de Telegram.
    """
    print("🚀 [SISTEMA] Enviador iniciado.")
    
    while True:
        # Tomar el siguiente video de la cola
        paquete = cola_produccion.get()
        
        # Si recibimos None, es que el Productor terminó
        if paquete is None:
            break
        
        n = paquete['n']
        path = paquete['path']
        caption = paquete['caption']
        
        try:
            print(f"📤 [ENVÍO] Subiendo Capítulo {n}...")
            # Llamada al despachador con reintentos configurado en enviar.py
            exito = enviar.despachar_a_telegram(path, caption)
            
            if exito:
                print(f"🏁 [ENVÍO] Capítulo {n} completado con éxito.")
            else:
                print(f"⚠️ [ENVÍO] No se pudo subir el Capítulo {n} tras los reintentos.")
                
        finally:
            # Sincronización de Memoria: El archivo se borra SIEMPRE tras el intento
            if os.path.exists(path):
                os.remove(path)
            cola_produccion.task_done()
    
    print("✅ [ENVÍO] Todos los archivos de la cola han sido procesados.")

def motor_mallycuts_express(p_vid, p_port, nombre, desc):
    """
    El Orquestador Central: Sincroniza todos los cerebros.
    """
    # 1. Análisis del video original
    try:
        res = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', p_vid
        ], capture_output=True, text=True)
        
        duracion_segundos = float(res.stdout)
        total_caps = int(duracion_segundos // config.CLIP_DURATION)
        if duracion_segundos % config.CLIP_DURATION > 0:
            total_caps += 1
            
    except Exception as e:
        print(f"❌ Error al analizar duración: {e}")
        return

    # 2. Inicialización del Logger Imperial
    mally_log = logger.MallyLogger(nombre, total_caps)
    
    # 3. Disparo de Portada (Sincrónico para marcar el inicio en el canal)
    try:
        with open(p_port, 'rb') as img:
            enviar.bot.send_photo(
                config.CHAT_ID, 
                img, 
                caption=mally_log.portada_msg(desc), 
                parse_mode="HTML"
            )
        os.remove(p_port)
    except Exception as e:
        print(f"⚠️ Error al enviar portada: {e}")

    # 4. LANZAMIENTO DE CEREBROS EN PARALELO
    hilo_produccion = threading.Thread(
        target=trabajador_productor, 
        args=(p_vid, total_caps, mally_log)
    )
    hilo_envio = threading.Thread(
        target=trabajador_enviador
    )

    hilo_produccion.start()
    hilo_envio.start()

    # 5. ESPERA SINCRONIZADA
    # El script esperará aquí hasta que ambos hilos terminen
    hilo_produccion.join()
    hilo_envio.join()

    # 6. CIERRE DE MISIÓN
    try:
        enviar.bot.send_message(
            config.CHAT_ID, 
            mally_log.final(), 
            parse_mode="HTML"
        )
    except:
        print("⚠️ No se pudo enviar el reporte final a Telegram.")

    # Limpieza del video original para liberar espacio en el Xiaomi
    if os.path.exists(p_vid):
        os.remove(p_vid)
        
    print(f"👑 [SISTEMA] Misión '{nombre}' finalizada con éxito.")
