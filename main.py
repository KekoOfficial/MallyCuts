import ffmpeg, os, config, telebot, logger, editar

bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    try:
        # 1. VALIDACIÓN DE RUTAS (Evita el 'No such file')
        v_abs = os.path.abspath(video_path)
        p_abs = os.path.abspath(portada_path)

        if not os.path.exists(v_abs):
            logger.log_error(f"Video no encontrado: {os.path.basename(v_abs)}")
            return
        
        # Crear carpeta temporal si no existe
        if not os.path.exists(config.TEMP_FOLDER):
            os.makedirs(config.TEMP_FOLDER)

        # 2. LABORATORIO DE PORTADA
        portada_ready = os.path.join(config.TEMP_FOLDER, "ready.jpg")
        editar.preparar_portada_imperial(p_abs, portada_ready)
        
        # Log de inicio
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_ready)
        
        # 3. ANÁLISIS FFMPEG
        probe = ffmpeg.probe(v_abs)
        duration = float(probe['format']['duration'])
        clip_dur = 60
        total = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. PROCESAMIENTO Y ENVÍO
        for i in range(total):
            actual = i + 1
            out_p = os.path.join(config.TEMP_FOLDER, f"clip_{actual}.mp4")
            
            # Recorte con inyección de miniatura
            v_in = ffmpeg.input(v_abs, ss=i*clip_dur, t=clip_dur)
            p_in = ffmpeg.input(portada_ready)
            v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            
            try:
                (ffmpeg.output(v_final, v_in.audio, out_p, 
                               vcodec='libx264', preset='ultrafast', 
                               acodec='aac', pix_fmt='yuv420p',
                               loglevel="error")
                 .overwrite_output().run(capture_stdout=True, capture_stderr=True))
            except ffmpeg.Error as e:
                err_detail = e.stderr.decode().split('\n')[-2] if e.stderr else "Error en renderizado"
                logger.log_error(f"FFMPEG: {err_detail}")
                return

            # Obtener caption del logger y enviar
            caption_publico = logger.generar_caption(nombre, actual, total)
            with open(out_p, 'rb') as v:
                bot.send_video(config.CHAT_ID, v, 
                               caption=caption_publico, 
                               supports_streaming=True, 
                               timeout=150) # Tiempo extra para archivos grandes
            
            logger.notify_clip_sent(actual, total, nombre)
            
            # Limpiar clip procesado
            if os.path.exists(out_p): os.remove(out_p)

        # 5. LIMPIEZA FINAL
        logger.mision_cumplida(nombre, total)
        for f in [v_abs, p_abs, portada_ready]:
            if os.path.exists(f): os.remove(f)

    except Exception as e:
        logger.log_error(str(e))

if __name__ == "__main__":
    print("🧠 Sakura Brain V7.5 sincronizado. Listo para el despliegue, @OliDevX.")
