from flask import Flask, render_template, request, jsonify
import os, threading, subprocess, config
from cortar import ejecutar_corte
from enviar import encolar_video

app = Flask(__name__)
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

def flujo_produccion(ruta_v, nombre_s):
    # 1. Obtener duración real con ffprobe
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {ruta_v}"
    duracion = float(subprocess.check_output(cmd, shell=True))
    
    total_partes = int(duracion // 60) + (1 if duracion % 60 > 0 else 0)
    
    # 2. Bucle de corte (Esto es rápido)
    for i in range(total_partes):
        inicio = i * 60
        n_parte = i + 1
        ruta_out = os.path.join(config.UPLOAD_FOLDER, f"p{n_parte}_{os.path.basename(ruta_v)}")
        
        # Cortamos
        caption = ejecutar_corte(ruta_v, ruta_out, inicio, n_parte, total_partes, nombre_s)
        
        # Encolamos (el worker se encarga del orden)
        encolar_video(ruta_out, caption)

    # Al finalizar de encordar todo, borramos el original
    # os.remove(ruta_v) 

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        archivo = request.files.get("video")
        nombre = request.form.get("nombre", "Serie Sin Nombre")
        
        if archivo:
            ruta = os.path.join(config.UPLOAD_FOLDER, archivo.filename)
            archivo.save(ruta)
            
            # Lanzamos el proceso en un hilo separado para no bloquear la web
            threading.Thread(target=flujo_produccion, args=(ruta, nombre)).start()
            
            return jsonify({"status": "procesando", "msg": f"🚀 {nombre} está en producción..."})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
