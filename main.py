from flask import Flask, render_template, jsonify, request
import os, ffmpeg, config, cortes, enviar

app = Flask(__name__)

# Asegurar carpetas
for d in [config.UPLOAD_DIR, config.TEMP_DIR]:
    os.makedirs(d, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    v_file = request.files['video']
    s_name = request.form['name']
    
    path_orig = os.path.join(config.UPLOAD_DIR, v_file.filename)
    v_file.save(path_orig)
    
    # Obtener info
    probe = ffmpeg.probe(path_orig)
    duracion = float(probe['format']['duration'])
    partes = int(duracion // 60) + (1 if duracion % 60 > 0 else 0)

    for i in range(partes):
        out_clip = os.path.join(config.TEMP_DIR, f"clip_{i+1}.mp4")
        if cortes.procesar_segmento(path_orig, i*60, 60, out_clip):
            cap = f"🎬 {s_name}\n💎 CAPÍTULO: {i+1}/{partes}\n🔗 @MallySeries"
            enviar.enviar_video(out_clip, cap)
            if os.path.exists(out_clip): os.remove(out_clip)

    os.remove(path_orig)
    return jsonify({"message": f"Finalizado: {s_name}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT)
