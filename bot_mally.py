import os, subprocess, time, json
from contextlib import ExitStack
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)

def limpiar_html(texto):
    return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def procesar_ciclo():
    if not os.path.exists(config.INPUT_FOLDER): os.makedirs(config.INPUT_FOLDER)
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)

    archivos = [f for f in os.listdir(config.INPUT_FOLDER) if f.lower().endswith(('.mp4', '.mkv'))]
    
    for video in archivos:
        path_in = os.path.join(config.INPUT_FOLDER, video)
        nombre = limpiar_html(video)
        
        bot.send_message(config.CHAT_ID, f"📡 <b>¡Detección Galería!</b>\n<code>{nombre}</code>\nCorte: 3 Minutos", parse_mode="HTML")
        
        out_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
        subprocess.run(['ffmpeg', '-y', '-i', path_in, '-f', 'segment', '-segment_time', '180', '-reset_timestamps', '1', '-c', 'copy', out_pattern], check=True)
        
        clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
        
        for i, c in enumerate(clips, 1):
            p_v = os.path.join(config.TEMP_FOLDER, c)
            p_t = p_v.replace(".mp4", ".jpg")
            subprocess.run(['ffmpeg', '-y', '-i', p_v, '-ss', '00:00:01', '-vframes', '1', p_t], capture_output=True)

            with ExitStack() as stack:
                v_file = stack.enter_context(open(p_v, 'rb'))
                t_file = stack.enter_context(open(p_t, 'rb')) if os.path.exists(p_t) else None
                bot.send_video(config.CHAT_ID, v_file, thumb=t_file, caption=f"🎬 <b>{nombre}</b>\n💎 Parte: {i}/{len(clips)}", parse_mode="HTML")

            if os.path.exists(p_v): os.remove(p_v)
            if os.path.exists(p_t): os.remove(p_t)
            time.sleep(2)

        os.remove(path_in)
        bot.send_message(config.CHAT_ID, f"🏁 <b>Completado:</b> {nombre}", parse_mode="HTML")
