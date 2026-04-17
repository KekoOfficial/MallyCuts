from flask import Flask, render_template, jsonify, request
import ffmpeg, os, sys, telebot

# --- CONFIG ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"
FOTO_PORTADA = "foto.jpg" # La portada fija que usas siempre

sys.dont_write_bytecode = True
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def motor_sakura_v10(video_filename):
    try:
        v_abs = os.path.abspath(video_filename)
        p_abs = os.path.abspath(FOTO_PORTADA)

        if not os.path.exists(v_abs): return "Video no encontrado"

        probe = ffmpeg.probe(v_abs)
        duration = float(probe['format']['duration'])
        total = int(duration // 60) + (1 if duration % 60 > 0 else 0)

        for i in range(total):
            out = f"segmento_{i+1}.mp4"
            
            # Corte directo con Bitrate Blindado
            (ffmpeg.input(v_abs, ss=i*60, t=60)
             .overlay(ffmpeg.input(p_abs), enable='between(t,0,0.05)')
             .output(out, vcodec='libx264', preset='ultrafast', acodec='aac',
                     video_bitrate='3.8M', maxrate='4M', bufsize='6M',
                     pix_fmt='yuv420p', map_metadata=-1, loglevel="error")
             .overwrite_output().run(quiet=True))

            # Envío
            with open(out, 'rb') as f:
                bot.send_video(CHAT_ID, f, 
                               caption=f"🎬 MALLY CUTS\n💎 CAPÍTULO: {i+1}/{total}\n🔗 @MallySeries", 
                               supports_streaming=True, timeout=300)
            os.remove(out)
        
        # Opcional: Borrar original tras procesar
        # os.remove(v_abs) 
        return f"Misión Cumplida: {video_filename} enviado."
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    # Escanea la carpeta buscando archivos mp4 para la galería
    archivos = [f for f in os.listdir('.') if f.endswith('.mp4')]
    return render_template('index.html', videos=archivos)

@app.route('/run', methods=['POST'])
def run_task():
    data = request.get_json()
    video_seleccionado = data.get('video_file')
    resultado = motor_sakura_v10(video_seleccionado)
    return jsonify({"message": resultado})

if __name__ == '__main__':
    print("🌸 Galería Sakura iniciada en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)
