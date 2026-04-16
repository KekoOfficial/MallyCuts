import ffmpeg
import os
import config
import telebot
import logger
import editar
import time

# Inicialización del Bot
bot = telebot.TeleBot(config.BOT_TOKEN)

def motor_mallycuts_express(video_path, portada_path, nombre, descripcion):
    """
    Cerebro Central: Coordina edición, log y fragmentación.
    """
    try:
        # 1. LABORATORIO GRÁFICO (editar.py)
        # Sincroniza la portada al formato 1080x1920 (9:16)
        portada_ready = os.path.join(config.TEMP_FOLDER, "portada_final.jpg")
        if not editar.preparar_portada_imperial(portada_path, portada_ready):
            # Si falla la edición pro, usamos la original como respaldo
            portada_ready = portada_path

        # 2. CENTRO DE COMANDO (logger.py)
        # Registra el despliegue con telemetría de hardware (CPU, RAM, DSK)
        logger.registrar_despliegue_imperial(nombre, descripcion, portada_ready)
        
        # 3. ANÁLISIS DE VIDEO
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        clip_dur = 60  # Duración estándar para Reels/TikTok
        total_clips = int(duration // clip_dur) + (1 if duration % clip_dur > 0 else 0)

        # 4. CICLO DE FRAGMENTACIÓN Y ENVÍO
        for i in range(total_clips):
            inicio = i * clip_dur
            output_clip = os.path.join(config.TEMP_FOLDER, f"clip_{i+1}.mp4")
            
            # Configuración de entrada de video y portada
            v_in = ffmpeg.input(video_path, ss=inicio, t=clip_dur)
            p_in = ffmpeg.input(portada_ready)
            
            # Inyección de miniatura invisible (0.05 segundos)
            # Esto garantiza que Telegram/TikTok tome la portada como miniatura
            v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            
            # Renderizado Ultra-Rápido
            (
                ffmpeg.output(v_final, v_in.audio, output_clip, 
                              vcodec='libx264', preset='ultrafast', 
                              acodec='aac', strict='experimental')
                .overwrite_output()
                .run(quiet=True)
            )

            # Envío a Telegram con el formato de Mally Series
            with open(output_clip, 'rb') as v:
                caption = (
                    f"🎬 {nombre}\n"
                    f"💎 PARTE: {i+1} / {total_clips}\n"
                    f"✅ Contenido Verificado\n"
                    f"🔗 @MallySeries #UmbraeStudio"
                )
                bot.send_video(config.CHAT_ID, v, caption=caption, supports_streaming=True)
            
            # Notificación de progreso al logger
            logger.notify_clip_sent(i+1, total_clips, nombre)
            
            # Limpieza inmediata de clip temporal
            if os.path.exists(output_clip):
                os.remove(output_clip)

        # 5. FINALIZACIÓN DE MISIÓN
        logger.mision_cumplida(nombre, total_clips)
        
        # Limpieza de archivos base para liberar espacio en el Xiaomi
        for f in [video_path, portada_path, portada_ready]:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        error_msg = f"Fallo en el Cerebro Central: {str(e)}"
        print(f"❌ {error_msg}")
        logger.log_error(error_msg)

if __name__ == "__main__":
    print("🧠 Cerebro de Umbrae Studio en línea...")
