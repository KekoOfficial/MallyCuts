import os, subprocess, threading, time, bot_mally, config

def motor_descarga_y_corte(link, titulo_manual):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    # 1. Definir nombre de archivo temporal
    video_temp = os.path.join(config.TEMP_FOLDER, "video_descargado.mp4")
    
    bot_mally.enviar_texto(f"📥 <b>MALLY DOWNLOADER</b>\n\n🛰 <b>Enlace:</b> {link}\n⏳ <i>Descargando video...</i>")

    # 2. Ejecutar yt-dlp con tu comando optimizado
    try:
        subprocess.run([
            'yt-dlp', '-f', config.YTDL_OPTS, 
            '-N', str(config.THREADS), 
            '-o', video_temp, link
        ], check=True)
    except Exception as e:
        bot_mally.enviar_texto(f"❌ <b>Error de descarga:</b>\n{str(e)}")
        return

    # 3. Preparar carpeta de salida para clips
    nombre_limpio = "".join(c for c in titulo_manual if c.isalnum() or c in (' ', '-', '_')).strip()
    serie_folder = os.path.join(config.TEMP_FOLDER, nombre_limpio.replace(" ", "_"))
    if not os.path.exists(serie_folder): os.makedirs(serie_folder)

    # 4. Obtener duración para el contador
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_temp])
    total_partes = int(float(probe) // config.CLIP_DURATION) + 1

    bot_mally.enviar_texto(f"🎬 <b>PROCESANDO:</b> {nombre_limpio}\n📦 <b>Partes:</b> {total_partes}")

    # 5. Cortar en partes
    output_pattern = os.path.join(serie_folder, "parte_%03d.mp4")
    subprocess.run(['ffmpeg', '-y', '-i', video_temp, '-f', 'segment', '-segment_time', str(config.CLIP_DURATION), '-reset_timestamps', '1', '-c', 'copy', output_pattern], capture_output=True)

    # 6. Despacho a Telegram (Lógica que ya conoces)
    enviados = 0
    while enviados < total_partes:
        archivos = sorted([f for f in os.listdir(serie_folder) if f.endswith('.mp4')])
        if len(archivos) > 1 or (enviados == total_partes - 1 and len(archivos) == 1):
            file_v = os.path.join(serie_folder, archivos[0])
            file_t = file_v.replace(".mp4", ".jpg")
            enviados += 1
            subprocess.run(['ffmpeg', '-y', '-i', file_v, '-ss', '1', '-vframes', '1', file_t], capture_output=True)
            
            caption = f"🎬 <b>{nombre_limpio}</b>\n💎 Parte {enviados}/{total_partes}\n📡 @MallySeries"
            bot_mally.enviar_clip(file_v, file_t, caption)
            
            os.remove(file_v); os.remove(file_t)
            time.sleep(3)
        else:
            time.sleep(5)

    # 7. LIMPIEZA FINAL (Clave para no llenar el cel)
    bot_mally.enviar_texto(f"🏁 <b>{nombre_limpio}</b> lista en el canal.")
    if os.path.exists(video_temp): os.remove(video_temp)
