import os, sys, ffmpeg, config, logger, cortes, enviar

# 🚫 ANULACIÓN DE BYTECODE: Mantener el sistema limpio
sys.dont_write_bytecode = True

def motor_sakura_core(video_path, portada_path, nombre, descripcion):
    try:
        # 1. Rutas Absolutas
        v_abs = os.path.abspath(video_path)
        p_abs = os.path.abspath(portada_path)

        if not os.path.exists(v_abs) or not os.path.exists(p_abs):
            logger.log_error("Faltan archivos base para la misión.")
            return

        # 2. Log de Despliegue
        logger.registrar_despliegue_imperial(nombre, descripcion, p_abs)
        
        # 3. Análisis de Tiempos
        probe = ffmpeg.probe(v_abs)
        duration = float(probe['format']['duration'])
        clip_dur = 60 
        total = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. Ciclo de Ejecución Sincronizado
        for i in range(total):
            actual = i + 1
            out_p = os.path.join(config.TEMP_FOLDER, f"clip_{actual}.mp4")
            
            # El Cerebro ordena a 'cortes.py' procesar
            exito = cortes.procesar_segmento(v_abs, p_abs, out_p, i*clip_dur, clip_dur)
            
            if exito:
                # El Cerebro ordena a 'enviar.py' subir
                caption = logger.generar_caption(nombre, actual, total)
                enviar.subir_video(out_p, caption)
                
                # Reporte al operador
                logger.notify_clip_sent(actual, total, nombre)
                
                # Limpieza inmediata de disco
                if os.path.exists(out_p): os.remove(out_p)
            else:
                logger.log_error(f"Fallo en segmento {actual}")

        # 5. Misión Cumplida y Purga Final
        logger.mision_cumplida(nombre, total)
        for f in [v_abs, p_abs]:
            if os.path.exists(f): os.remove(f)

    except Exception as e:
        logger.log_error(str(e))

if __name__ == "__main__":
    print("🧠 Cerebro Umbrae V9.0 Sincronizado. Operativo.")
