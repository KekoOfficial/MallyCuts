import os, sys, ffmpeg, config, logger, cortes, enviar

sys.dont_write_bytecode = True

def motor_sakura_core(video_path, portada_path, nombre, descripcion):
    try:
        v_abs, p_abs = os.path.abspath(video_path), os.path.abspath(portada_path)
        if not os.path.exists(v_abs): return logger.log_error("Video no encontrado")

        logger.registrar_despliegue_imperial(nombre, descripcion, p_abs)
        
        probe = ffmpeg.probe(v_abs)
        total = int(float(probe['format']['duration']) // config.CLIP_DURATION) + 1

        for i in range(total):
            actual = i + 1
            out_p = os.path.join(config.TEMP_FOLDER, f"segmento_{actual}.mp4")
            
            if cortes.procesar_segmento(v_abs, p_abs, out_p, i*config.CLIP_DURATION):
                caption = logger.generar_caption(nombre, actual, total)
                if enviar.subir_video(out_p, caption):
                    logger.notify_clip_sent(actual, total, nombre)
                
                if os.path.exists(out_p): os.remove(out_p)
        
        logger.mision_cumplida(nombre, total)
        for f in [v_abs, p_abs]: 
            if os.path.exists(f): os.remove(f)

    except Exception as e:
        logger.log_error(str(e))

if __name__ == "__main__":
    print(f"🧠 Umbrae Core V9.1 | Folder: {config.TEMP_FOLDER} | @OliDevX")
