import os
import sys
import time
from moviepy.editor import VideoFileClip # Importación para cortes automáticos
# Importa la infraestructura unificada y el logger
try:
    import config as cfg
    import logger
    # enviar y marcas se importan aquí para mayor sincronización del hilo
    import marcas 
    import enviar
except ImportError:
    print("❌ Errorcortes: Faltan config.py, logger.py, marcas.py o enviar.py.")
    sys.exit(1)

def orquestar_produccion_sincronizada(video_path, portada_path, nombre_serie, descripcion, job_semaphore):
    """
    HILO SEPARADO DELEGADO: Corta el video, aplica marca de agua, optimiza y envía a Telegram.
    Protege el procesador de Termux usando el semáforo pasado por main.py.
    """
    with job_semaphore: # Asegura que solo corra un renderizado a la vez en el core
        logger.registrar_log(f"🛠️ [PROCESO MASTER] Iniciando ciclo de media sincronizado de: {nombre_serie}...")
        
        try:
            # 1. --- ANALIZAR VIDEO ORIGINAL (antiguo cortes.py) ---
            logger.registrar_log(f"🎬 [CORTES] Analizando video original para auto-corte en {cfg.NUM_SEGMENTS_AUTOCUT} partes...")
            clip = VideoFileClip(video_path)
            duracion_total = clip.duration
            clip.close() # Cerrar clip original para liberar recursos
            
            duracion_segmento = duracion_total / cfg.NUM_SEGMENTS_AUTOCUT
            logger.registrar_log(f"🎬 [CORTES] Duración total: {duracion_total:.2f}s | Segmentos de {duracion_segmento:.2f}s")
            
            for chapter in range(1, cfg.NUM_SEGMENTS_AUTOCUT + 1):
                logger.registrar_log(f"🛠️ [PROCESO {chapter}/{cfg.NUM_SEGMENTS_AUTOCUT}] Iniciando ciclo completo para Capítulo {chapter}...")
                
                # Definir tiempos de corte
                start_time = (chapter - 1) * duracion_segmento
                
                filename = os.path.basename(video_path)
                name_part, ext = os.path.splitext(filename)
                # Nombre único para el segmento procesado
                # Usamos secure_filename ya aplicado en main.py para mayor sincronización
                output_filename = f"PROCESADO_{name_part}_Cap{chapter}{ext}"
                output_path = os.path.join(cfg.PRODUCTION_FOLDER, output_filename)
                
                # 2. --- DELEGAR MARCAS: (lógica marcas.py) ---
                # Pasamos los parámetros necesarios a marcas.py para el renderizado
                render_exitoso = marcas.aplicar_branding_ ffmpeg(video_path, output_path, start_time, duracion_segmento, chapter)
                
                if not render_exitoso:
                    raise Exception(f"Fallo el renderizado de FFmpeg en Capítulo {chapter}. Abortando ciclo.")
                    
                logger.registrar_log(f"✅ [FFMPEG CAP{chapter}] Capítulo renderizado con éxito: {output_filename}")
                
                # 3. --- DELEGAR DISTRIBUCIÓN: (lógica enviar.py) ---
                # Pasamos los parámetros necesarios a enviar.py para la subida
                subida_exitosa = enviar.subir_media_telegram(output_path, portada_path, nombre_serie, descripcion, chapter)
                
                # --- LIMPIEZA DE ARCHIVO PROCESADO (Segmento) ---
                if subida_exitosa:
                    try:
                        os.remove(output_path)
                        logger.registrar_log(f"🧹 [LIMPIEZA CAP{chapter}] Segmento procesado eliminado.")
                    except OSError as e:
                        logger.registrar_log(f"⚠️ [LIMPIEZA] Error eliminando segmento: {str(e)}")
                
                # Pausa táctica entre capítulos para no "inundar" Telegram (FloodWait)
                logger.registrar_log(f"⚡ [COOLDOWN] Esperando {cfg.PAUSA_ENTRE_CAPS}s antes del siguiente segmento...")
                time.sleep(cfg.PAUSA_ENTRE_CAPS)
            
            # 4. --- LIMPIEZA FINAL DE ARCHIVOS ORIGINALES ---
            logger.registrar_log(f"🏆 [EXITO MAESTRO] Producción sincronizada de {nombre_serie} completada.")
            try:
                os.remove(video_path)
                os.remove(portada_path)
                logger.registrar_log(f"🧹 [LIMPIEZA FINAL] Archivos originales eliminados.")
            except OSError as e:
                logger.registrar_log(f"⚠️ [LIMPIEZA FINAL] Error eliminando originales: {str(e)}")
            
        except Exception as e:
            error_msg = f"❌ [ERROR CRÍTICO CORTES] Falló el ciclo de media de {nombre_serie}: {str(e)}"
            logger.registrar_log(error_msg)
