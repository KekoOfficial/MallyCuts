import os, subprocess, threading, time, bot_mally, config
from yt_dlp import YoutubeDL

def motor_principal(link, titulo):
    # 1. Descarga Directa
    bot_mally.enviar_msg(f"📥 <b>MALLY CLOUD</b>\n\n🛰 <b>Link:</b> {link}\n⏳ Descargando video...")
    
    video_path = os.path.join(config.TEMP_FOLDER, "original.mp4")
    
    try:
        opts = config.YTDL_OPTS.copy()
        opts['outtmpl'] = video_path
        with YoutubeDL(opts) as ydl:
            ydl.download([link])
    except Exception as e:
        bot_mally.enviar_msg(f"❌ Error yt-dlp: {e}")
        return

    # 2. Carpeta de Serie
    nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_')).strip()
    serie_folder = os.path.join(config.TEMP_FOLDER, nombre_limpio.replace(" ", "_"))
    if not os.path.exists(serie_folder): os.makedirs(serie_folder)

    # 3. Analizar y Segmentar
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path])
    total = int(float(probe) // config.CLIP_DURATION) + 1
    bot_mally.enviar_msg(f"🎬 <b>PROCESANDO:</b> {nombre_limpio}\n📦 <b>Partes:</b> {total}")

    pattern = os.path.join(serie_folder, "p_%03d.mp4")
    subprocess.run(['ffmpeg', '-y', '-i', video_path, '-f', 'segment', '-segment_time', str(config.CLIP_DURATION), '-c:v', 'copy', '-c:a', 'copy', pattern], capture_output=True)

    # 4. Despacho
    enviados = 0
    while enviados < total:
        clips = sorted([f for f in os.listdir(serie_folder) if f.endswith('.mp4')])
        if len(clips) > 1 or (enviados == total - 1 and len(clips) == 1):
            v_p = os.path.join(serie_folder, clips[0])
            t_p = v_p.replace(".mp4", ".jpg")
            enviados += 1
            
            subprocess.run(['ffmpeg', '-y', '-i', v_p, '-ss', '1', '-vframes', '1', t_p], capture_output=True)
            cap = f"🎬 <b>{nombre_limpio}</b>\n💎 Parte {enviados}/{total}\n📡 @MallySeries"
            
            try:
                bot_mally.enviar_clip(v_p, t_p, cap)
            except:
                time.sleep(10)
            
            if os.path.exists(v_p): os.remove(v_p)
            if os.path.exists(t_p): os.remove(t_p)
            time.sleep(config.SLEEP_BETWEEN_POSTS)
        else:
            time.sleep(5)

    bot_mally.enviar_msg(f"🏁 <b>{nombre_limpio}</b> finalizada con éxito.")
    if os.path.exists(video_path): os.remove(video_path)
