import os, subprocess, threading, time, bot_mally, config

def motor_procesamiento(video_input, titulo):
    # Limpiar y crear carpeta
    nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_')).strip()
    folder = os.path.join(config.TEMP_FOLDER, nombre_limpio.replace(" ", "_"))
    if not os.path.exists(folder): os.makedirs(folder)

    # 1. Obtener duración y calcular partes
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_input])
    total_partes = int(float(probe) // config.CLIP_DURATION) + 1

    bot_mally.enviar_texto(f"🎬 <b>MALLY SERIES</b>\n\n🚀 <b>INICIANDO:</b> {nombre_limpio}\n📦 <b>Partes estimadas:</b> {total_partes}")

    # 2. Iniciar Corte (FFmpeg)
    output_pattern = os.path.join(folder, "parte_%03d.mp4")
    subprocess.run(['ffmpeg', '-y', '-i', video_input, '-f', 'segment', '-segment_time', str(config.CLIP_DURATION), '-reset_timestamps', '1', '-c', 'copy', output_pattern], capture_output=True)

    # 3. Despachador Organizado
    enviados = 0
    while enviados < total_partes:
        archivos = sorted([f for f in os.listdir(folder) if f.endswith('.mp4')])
        
        # Enviamos si hay un archivo listo y FFmpeg ya saltó al siguiente
        if len(archivos) > 1 or (enviados == total_partes - 1 and len(archivos) == 1):
            file_v = os.path.join(folder, archivos[0])
            file_t = file_v.replace(".mp4", ".jpg")
            enviados += 1

            # Generar miniatura
            subprocess.run(['ffmpeg', '-y', '-i', file_v, '-ss', '00:00:01', '-vframes', '1', file_t], capture_output=True)

            caption = f"🎬 <b>MALLY SERIES</b>\n\n📂 <b>{nombre_limpio}</b>\n💎 Parte {enviados}/{total_partes}\n📡 @MallySeries"

            for _ in range(config.MAX_RETRIES):
                try:
                    bot_mally.enviar_clip(file_v, file_t, caption)
                    break
                except: time.sleep(10)

            # Limpieza inmediata
            if os.path.exists(file_v): os.remove(file_v)
            if os.path.exists(file_t): os.remove(file_t)
            time.sleep(config.SLEEP_BETWEEN_POSTS)
        else:
            time.sleep(5)

    bot_mally.enviar_texto(f"🏁 <b>{nombre_limpio}</b>\n✅ Temporada Completa")
    if os.path.exists(video_input): os.remove(video_input)
