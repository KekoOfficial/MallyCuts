import ffmpeg
import os
import config
import telebot
import logger
import editar

# Inicialización del Núcleo Imperial
bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    """
    Cerebro Central: Ejecuta la lógica de fragmentación y distribución.
    Optimizado por @OliDevX para estabilidad en Termux.
    """
    try:
        # 1. LABORATORIO GRÁFICO (Optimización de Portada)
        portada_ready = os.path.join(config.TEMP_FOLDER, "ready.jpg")
        editar.preparar_portada_imperial(portada_path, portada_ready)
        
        # 2. LOG DE DESPLIEGUE (ADMIN)
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_ready)
        
        # 3. ANÁLISIS DE ESTRUCTURA
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        clip_dur = 60  # Segundos por clip
        total = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. CICLO DE FRAGMENTACIÓN
        for i in range(total):
            actual = i + 1
            out_p = os.path.join(config.TEMP_FOLDER, f"clip_{actual}.mp4")
            
            # Entradas de flujo
            v_in = ffmpeg.input(video_path, ss=i*clip_dur, t=clip_dur)
            p_in = ffmpeg.input(portada_ready)
            
            # Overlay de miniatura (0.05s) con escalado de compatibilidad
            v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            
            try:
                # Renderizado con parámetros de compatibilidad universal (YUV420P)
                (ffmpeg.output(v_final, v_in.audio, out_p, 
                               vcodec='libx264', preset='ultrafast', 
                               acodec='aac', pix_fmt='yuv420p',
                               map_metadata=-1) # Limpia metadatos para evitar errores
                 .overwrite_output().run(capture_stdout=True, capture_stderr=True))
            except ffmpeg.Error as e:
                # Captura el error específico de ffmpeg para el logger
                error_msg = e.stderr.decode().split('\n')[-2] if e.stderr else "Error interno de FFMPEG"
                logger.log_error(f"FFMPEG: {error_msg}")
                return

            # 5. DISTRIBUCIÓN SINCRONIZADA
            # Solicitamos el caption estético al logger
            caption_publico = logger.generar_caption(nombre, actual, total)
            
            with open(out_p, 'rb') as v:
                bot.send_video(
                    config.CHAT_ID, 
                    v, 
                    caption=caption_publico, 
                    supports_streaming=True, 
                    timeout=120 # Tiempo extra para evitar TimeoutError
                )
            
            # Notificación de progreso administrativo
            logger.notify_clip_sent(actual, total, nombre)
            
            # Limpieza inmediata de clip temporal
            if os.path.exists(out_p):
                os.remove(out_p)

        # 6. FINALIZACIÓN Y LIMPIEZA DE NÚCLEO
        logger.mision_cumplida(nombre, total)
        
        # Purga de archivos originales
        for f in [video_path, portada_path, portada_ready]:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        # Reporte de fallo general al operador @OliDevX
        logger.log_error(str(e))

if __name__ == "__main__":
    print("🧠 Cerebro Umbrae @OliDevX sincronizado y listo.")
