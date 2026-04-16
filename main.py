import ffmpeg
import os
import config
import telebot
import logger
import editar

# Inicialización del Núcleo
bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    """
    Cerebro Central: Ejecuta la lógica de procesamiento y distribución.
    Diseñado por @OliDevX.
    """
    try:
        # 1. LABORATORIO GRÁFICO
        # Ajusta la portada al estándar 9:16 antes de procesar el video
        portada_ready = os.path.join(config.TEMP_FOLDER, "ready.jpg")
        editar.preparar_portada_imperial(portada_path, portada_ready)
        
        # 2. LOG DE DESPLIEGUE (ADMIN)
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_ready)
        
        # 3. ANÁLISIS TÉCNICO
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        clip_dur = 60  # Duración de cada segmento
        total = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. CICLO DE PROCESAMIENTO
        for i in range(total):
            actual = i + 1
            out_p = os.path.join(config.TEMP_FOLDER, f"clip_{actual}.mp4")
            
            # Recorte e Inyección de Miniatura (0.05s)
            v_in = ffmpeg.input(video_path, ss=i*clip_dur, t=clip_dur)
            p_in = ffmpeg.input(portada_ready)
            v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            
            (ffmpeg.output(v_final, v_in.audio, out_p, 
                           vcodec='libx264', preset='ultrafast', 
                           acodec='aac')
             .overwrite_output().run(quiet=True))

            # 5. DISTRIBUCIÓN
            # El main solicita el caption estético al logger
            caption_publico = logger.generar_caption(nombre, actual, total)
            
            with open(out_p, 'rb') as v:
                bot.send_video(
                    config.CHAT_ID, 
                    v, 
                    caption=caption_publico, 
                    supports_streaming=True, 
                    timeout=120
                )
            
            # Reporte de progreso administrativo
            logger.notify_clip_sent(actual, total, nombre)
            
            # Limpieza de residuo temporal
            if os.path.exists(out_p):
                os.remove(out_p)

        # 6. FINALIZACIÓN DE TAREA
        logger.mision_cumplida(nombre, total)
        
        # Purga de archivos originales para liberar espacio en el Xiaomi
        for f in [video_path, portada_path, portada_ready]:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        # Reporte de error al operador @OliDevX
        logger.log_error(str(e))

if __name__ == "__main__":
    print("🧠 Cerebro Umbrae @OliDevX operativo.")
