from flask import Flask, render_template, jsonify, request
import os, ffmpeg, cortes, enviar

app = Flask(__name__)
FOTO_PORTADA = "foto.jpg"

@app.route('/')
def home():
    videos = []
    if not os.path.exists('static/thumbs'): os.makedirs('static/thumbs')
    for f in os.listdir('.'):
        if f.endswith('.mp4'):
            thumb = f.replace('.mp4', '.jpg')
            t_path = os.path.join('static/thumbs', thumb)
            if not os.path.exists(t_path):
                try: (ffmpeg.input(f, ss=1).filter('scale', 400, -1).output(t_path, vframes=1).run(quiet=True))
                except: pass
            videos.append({'name': f, 'thumb': thumb})
    return render_template('index.html', videos=videos)

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    v_file = data.get('video_file')
    s_name = data.get('serie_name')
    
    probe = ffmpeg.probe(v_file)
    duracion_total = float(probe['format']['duration'])
    partes = int(duracion_total // 60) + (1 if duracion_total % 60 > 0 else 0)

    for i in range(partes):
        out = f"temp_clip.mp4"
        if cortes.procesar_segmento(v_file, FOTO_PORTADA, i*60, 60, out):
            caption = f"🎬 {s_name}\n💎 CAPÍTULO: {i+1}/{partes}\n🔗 @MallySeries"
            enviar.enviar_video(out, caption)
            if os.path.exists(out): os.remove(out)
            
    return jsonify({"message": f"Serie {s_name} completada"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
