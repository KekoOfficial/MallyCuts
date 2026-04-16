import ffmpeg, os, config, telebot
import logger, editar

bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    try:
        # 1. Optimización Gráfica
        portada_ready = os.path.join(config.TEMP_FOLDER, "ready.jpg")
        editar.preparar_portada_imperial(portada_path, portada_ready)
        
        # 2. Notificación de Inicio
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_ready)
        
        # 3. Análisis de Video
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        clip_dur = 60
        total = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. Ciclo de Fragmentación
        for i in range(total):
            out_p = os.path.join(config.TEMP_FOLDER, f"clip_{i+1}.mp4")
            v_in = ffmpeg.input(video_path, ss=i*clip_dur, t=clip_dur)
            p_in = ffmpeg.input(portada_ready)
            
            # Portada de 0.05s (Miniatura automática)
            final_v = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            
            (ffmpeg.output(final_v, v_in.audio, out_p, 
                           vcodec='libx264', preset='ultrafast', 
                           acodec='aac')
             .overwrite_output().run(quiet=True))

            # Envío de Clip
            with open(out_p, 'rb') as v:
                cap = f"🎬 {nombre} - Parte {i+1}\n✅ Contenido Verificado\n🔗 @MallySeries"
                bot.send_video(config.CHAT_ID, v, caption=cap, supports_streaming=True)
            
            logger.notify_clip_sent(i+1, total, nombre)
            if os.path.exists(out_p): os.remove(out_p)

        # 5. Cierre de Operación
        logger.mision_cumplida(nombre, total)
        
        # Limpieza de archivos originales
        for f in [video_path, portada_path, portada_ready]:
            if os.path.exists(f): os.remove(f)

    except Exception as e:
        logger.log_error(str(e))
