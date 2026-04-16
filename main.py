import ffmpeg
import os
import time
import config
import telebot

# Conexión con el Bot de Telegram
bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    """
    Motor V4.5: Envía kit de prensa primero, luego clips con miniatura invisible.
    """
    try:
        print(f"\n[🚀] INICIANDO DESPLIEGUE: {nombre}")
        
        # --- PASO 1: ENVIAR PORTADA Y TÍTULOS PRIMERO ---
        # Esto sirve para que en Telegram veas primero de qué trata el proyecto.
        with open(portada_path, 'rb') as p:
            mensaje_principal = (
                f"🗂️ **NUEVO PROYECTO: {nombre}**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 **DESCRIPCIÓN:**\n{descripcion}\n\n"
                f"👑 **Creador:** Noa | Umbrae Studio\n"
                f"📅 **Fecha:** {time.strftime('%d/%m/%Y')}"
            )
            bot.send_photo(config.CHAT_ID, p, caption=mensaje_principal, parse_mode='Markdown')
        
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
            
            print(f"[🎬] Creando Clip {i+1}/{total_clips}...")

            # Definimos las entradas
            input_video = ffmpeg.input(video_path, ss=start_time, t=clip_duration)
            # Escalamos la portada al formato estándar de TikTok (1080x1920)
            input_cover = ffmpeg.input(portada_path).filter('scale', 1080, 1920)

            # Inyectamos la portada solo 0.05 segundos (invisible pero detectable por TikTok)
            video_final = ffmpeg.overlay(
                input_video, 
                input_cover, 
                enable='between(t,0,0.05)'
            )

            # Renderizado Ultra-Rápido
            (
                ffmpeg
                .output(video_final, input_video.audio, output_path, 
                        vcodec='libx264', preset='ultrafast', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )

            # --- PASO 4: ENVIAR CLIPS ---
            with open(output_path, 'rb') as v:
                caption_clip = f"🎬 {nombre} - Parte {i+1}\n🚀 Listo para publicar"
                bot.send_video(config.CHAT_ID, v, caption=caption_clip, supports_streaming=True)
            
            # Limpieza inmediata de clip enviado
            if os.path.exists(output_path):
                os.remove(output_path)

        # --- PASO 5: LIMPIEZA FINAL ---
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(portada_path): os.remove(portada_path)
        
        print(f"\n[✅] TODO ENVIADO: {nombre} ya está en Telegram.")

    except Exception as e:
        print(f"[🔥] ERROR EN EL MOTOR: {str(e)}")

