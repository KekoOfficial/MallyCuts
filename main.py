import os
import subprocess
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)

def segmentar_video(input_path, chat_id):
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)

    # Aviso de inicio
    bot.send_message(chat_id, "⚙️ **Motor Chrome Magic Good**: Iniciando segmentación ultra-rápida...")

    # Comando FFmpeg Optimizado
    output_pattern = os.path.join(config.TEMP_FOLDER, "segmento_%03d.mp4")
    
    comando = [
        'ffmpeg', '-i', input_path,
        '-f', 'segment',
        '-segment_time', str(config.CLIP_DURATION),
        '-reset_timestamps', '1',
        '-c', 'copy', # MÁXIMA VELOCIDAD: No renderiza, solo corta
        output_pattern
    ]

    try:
        subprocess.run(comando, check=True, capture_output=True)
        
        # Envío ordenado
        segmentos = sorted(os.listdir(config.TEMP_FOLDER))
        for seg in segmentos:
            path_seg = os.path.join(config.TEMP_FOLDER, seg)
            bot.send_message(chat_id, f"📤 **Enviando:** {seg}")
            with open(path_seg, 'rb') as v:
                bot.send_video(chat_id, v)
            os.remove(path_seg) # Limpieza en tiempo real

        bot.send_message(chat_id, "✅ **Proceso Global Finalizado.**")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error en el motor: {e}")

@bot.message_handler(content_types=['video'])
def recibir_video(message):
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    input_file = "input_video.mp4"
    with open(input_file, 'wb') as f:
        f.write(downloaded_file)
    
    segmentar_video(input_file, message.chat.id)
    if os.path.exists(input_file): os.remove(input_file)

if __name__ == "__main__":
    print("🚀 Chrome Magic Good V2 - Online")
    bot.polling()
