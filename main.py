import ffmpeg
import os
import time
import config
import telebot

# Inicialización del Bot Imperial
bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    """
    Motor principal: Corta videos e inyecta la portada en el frame inicial 
    de cada segmento para automatización total en TikTok/Reels.
    """
    try:
        print(f"\n[🚀] INICIANDO DESPLIEGUE: {nombre}")
        
        # 1. Obtener duración total del video
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        
        # 2. Configurar tiempos (60s por clip según tu estándar)
        clip_duration = 60 
        total_clips = int(duration // clip_duration) + (1 if duration % clip_duration > 0 else 0)
        
        print(f"[📊] Total a procesar: {total_clips} clips de {clip_duration}s")

        for i in range(total_clips):
            start_time = i * clip_duration
            output_name = f"Clip_{i+1}_{nombre.replace(' ', '_')}.mp4"
            output_path = os.path.join(config.TEMP_FOLDER, output_name)
            
            print(f"[🎬] Procesando Clip {i+1}/{total_clips}...")

            # --- LÓGICA DE INYECCIÓN DE PORTADA (EL TRUCO TIKTOK) ---
            # Tomamos el video y la portada
            input_video = ffmpeg.input(video_path, ss=start_time, t=clip_duration)
            input_cover = ffmpeg.input(portada_path)

            # Overlay: La portada se pone encima solo durante los primeros 0.2 segundos
            # Esto engaña al algoritmo de TikTok para usarla como miniatura
            video_with_cover = ffmpeg.overlay(
                input_video, 
                input_cover, 
                enable='between(t,0,0.2)'
            )

            # Renderizado Ultra-Rápido para Termux
            try:
                (
                    ffmpeg
                    .output(video_with_cover, input_video.audio, output_path, 
                            vcodec='libx264', preset='ultrafast', acodec='copy')
                    .overwrite_output()
                    .run(quiet=True)
                )
            except ffmpeg.Error as e:
                print(f"[❌] Error en FFmpeg: {e}")
                continue

            # 3. Envío Automático a Telegram
            with open(output_path, 'rb') as v:
                caption = f"🎬 {nombre} - Parte {i+1}\n\n📝 {descripcion}\n\n👑 Creador: Noa | Umbrae Studio"
                bot.send_video(config.CHAT_ID, v, caption=caption, supports_streaming=True)
            
            print(f"[✅] Clip {i+1} enviado exitosamente.")
            
            # Limpieza de residuo para no llenar el Xiaomi
            if os.path.exists(output_path):
                os.remove(output_path)

        # Limpieza de archivos originales tras procesar todo
        os.remove(video_path)
        os.remove(portada_path)
        print(f"\n[👑] MISIÓN CUMPLIDA: {nombre} desplegado al 100%.")

    except Exception as e:
        print(f"[🔥] ERROR CRÍTICO EN EL MOTOR: {str(e)}")

