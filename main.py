import ffmpeg
import os
import sys
import telebot
import time

# --- CONFIGURACIÓN INTEGRADA (Anulamos config.py externo para evitar fallos) ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"
TEMP_FOLDER = "mally_studio_segments"
CLIP_DURATION = 60
WATERMARK_TEXT = "t.me/MallySeries"

# 🚫 BLOQUEO DE RESIDUOS
sys.dont_write_bytecode = True
bot = telebot.TeleBot(BOT_TOKEN)

def motor_imperial_directo(video_name, portada_name, serie_titulo):
    """
    Motor Lineal de @OliDevX: Corta -> Envía -> Siguiente.
    """
    try:
        # 1. Preparación de Entorno
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
            
        v_abs = os.path.abspath(video_name)
        p_abs = os.path.abspath(portada_name)

        if not os.path.exists(v_abs):
            print(f"❌ Error: No encuentro el video {video_name}")
            return

        # 2. Análisis de duración
        probe = ffmpeg.probe(v_abs)
        duration = float(probe['format']['duration'])
        total_clips = int(duration // CLIP_DURATION) + (1 if duration % CLIP_DURATION > 0 else 0)

        print(f"🌸 SAKURA SYSTEM | Iniciando: {serie_titulo}")
        print(f"📊 Total de fragmentos a generar: {total_clips}")

        # 3. Ciclo de Ejecución Lineal (Corta y Manda)
        for i in range(total_clips):
            actual = i + 1
            out_p = os.path.join(TEMP_FOLDER, f"clip_{actual}.mp4")
            inicio = i * CLIP_DURATION

            print(f"🎬 [{actual}/{total_clips}] Cortando...")

            # --- PROCESAMIENTO FFMPEG (Blindado Anti-413) ---
            v_in = ffmpeg.input(v_abs, ss=inicio, t=CLIP_DURATION)
            p_in = ffmpeg.input(p_abs)
            
            # Overlay de portada (0.05s) + Marca de agua
            v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
            v_final = v_final.drawtext(
                text=WATERMARK_TEXT, 
                x='main_w-text_w-15', y='main_h-text_h-15',
                fontsize=32, fontcolor='white@0.5',
                shadowcolor='black', shadowx=2, shadowy=2
            )

            # Salida con bitrate controlado (Aprox 30MB por clip)
            (ffmpeg.output(v_final, v_in.audio, out_p, 
                           vcodec='libx264', preset='ultrafast', acodec='aac',
                           video_bitrate='3.8M', maxrate='4M', bufsize='6M',
                           pix_fmt='yuv420p', map_metadata=-1, loglevel="error")
             .overwrite_output().run(quiet=True))

            # --- ENVÍO AL CANAL ---
            print(f"📤 [{actual}/{total_clips}] Enviando a Telegram...")
            caption = (f"🎬 {serie_titulo}\n"
                       f"💎 CAPÍTULO: {actual} / {total_clips}\n"
                       f"✅ Contenido Verificado\n"
                       f"🔗 @MallySeries #UmbraeStudio")

            try:
                with open(out_p, 'rb') as v:
                    bot.send_video(CHAT_ID, v, caption=caption, 
                                   supports_streaming=True, timeout=300)
                print(f"✨ Clip {actual} enviado con éxito.")
            except Exception as e:
                print(f"💔 Error al enviar: {e}")

            # Limpieza inmediata de RAM y Disco
            if os.path.exists(out_p):
                os.remove(out_p)

        # 4. Purga Final
        print("🧹 Limpiando archivos originales...")
        os.remove(v_abs)
        os.remove(p_abs)
        print("✅ MISIÓN CUMPLIDA. @OliDevX")

    except Exception as e:
        print(f"❌ CRITICAL FAULT: {e}")

if __name__ == "__main__":
    # --- INTERFAZ DE USUARIO RÁPIDA ---
    # Solo cambia estos 3 valores antes de ejecutar
    VIDEO_ARCHIVO = "video.mp4" 
    PORTADA_ARCHIVO = "foto.jpg"
    TITULO_SERIE = "MALLY CUTS"

    motor_imperial_directo(VIDEO_ARCHIVO, PORTADA_ARCHIVO, TITULO_SERIE)
