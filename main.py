from flask import Flask, render_template, jsonify, request
import os, ffmpeg, cortes, enviar

app = Flask(__name__)
FOTO_ESTATICA = "foto.jpg" # La portada que usará siempre el sistema
THUMB_DIR = "static/thumbs"

@app.route('/')
def home():
    if not os.path.exists(THUMB_DIR): os.makedirs(THUMB_DIR)
    videos = []
    for f in os.listdir('.'):
        if f.endswith('.mp4'):
            thumb = f.replace('.mp4', '.jpg')
            t_path = os.path.join(THUMB_DIR, thumb)
            if not os.path.exists(t_path):
                try: 
                    (ffmpeg.input(f, ss=1).filter('scale', 400, -1)
                     .output(t_path, vframes=1).run(quiet=True))
                except: pass
            videos.append({'name': f, 'thumb': thumb})
    return render_template('index.html', videos=videos)

@app.route('/run', methods=['POST'])
def run_task():
    data = request.get_json()
    v_file = data.get('video_file')
    s_name = data.get('serie_name')
    
    # Obtener duración y calcular partes
    probe = ffmpeg.probe(v_file)
    total_sec = float(probe['format']['duration'])
    partes = int(total_sec // 60) + (1 if total_sec % 60 > 0 else 0)

    for i in range(partes):
        out = f"temp_segmento.mp4"
        # Llama al módulo de cortes
        if cortes.procesar_segmento(v_file, FOTO_ESTATICA, i*60, 60, out):
            caption = f"🎬 {s_name}\n💎 CAPÍTULO: {i+1}/{partes}\n🔗 @MallySeries"
            # Llama al módulo de envío
            enviar.enviar_video(out, caption)
            if os.path.exists(out): os.remove(out)
            
    return jsonify({"message": f"Producción Finalizada: {s_name}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
