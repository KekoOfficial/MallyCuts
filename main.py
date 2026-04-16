import ffmpeg
import os
import time
import config
import telebot
import logger  # Importamos tu nuevo logger

bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    try:
        print(f"\n[🚀] INICIANDO MOTOR: {nombre}")
        
        # --- PASO 1: REGISTRO INICIAL (Kit de Prensa) ---
        # Llamamos al logger para que envíe la portada y el texto primero
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_path)
        
        # --- PASO 2: ANÁLISIS DE VIDEO ---
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        clip_duration = 60 
        total_clips = int(duration // clip_duration) + (1 if duration % clip_duration > 0 else 0)

        # --- PASO 3: PROCESAMIENTO DE CLIPS ---
        for i in range(total_clips):
            start_time = i * clip_duration
            output_name = f"Clip_{i+1}_{nombre.replace(' ', '_')}.mp4"
            output_path = os.path.join(config.TEMP_FOLDER, output_name)
            
            # Entradas: Video y Portada escalada a 1080x1920
            input_video = ffmpeg.input(video_path, ss=start_time, t=clip_duration)
            input_cover = ffmpeg.input(portada_path).filter('scale', 1080, 1920)

            # Inyección de miniatura (0.05s para que TikTok la vea pero no estorbe)
            video_final = ffmpeg.overlay(
                input_video, 
                input_cover, 
                enable='between(t,0,0.05)'
            )

            (
                ffmpeg
                .output(video_final, input_video.audio, output_path, 
                        vcodec='libx264', preset='ultrafast', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )

            # --- PASO 4: ENVÍO DE CLIPS ---
            with open(output_path, 'rb') as v:
                caption_clip = f"🎬 {nombre} - Parte {i+1}\n✅ Portada inyectada"
                bot.send_video(config.CHAT_ID, v, caption=caption_clip, supports_streaming=True)
            
            if os.path.exists(output_path):
                os.remove(output_path)

        # --- PASO 5: LIMPIEZA FINAL ---
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(portada_path): os.remove(portada_path)
        print(f"[✅] DESPLIEGUE FINALIZADO")

    except Exception as e:
        logger.log_error(str(e))
        print(f"[🔥] ERROR: {e}")
