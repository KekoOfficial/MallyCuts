from flask import Flask, render_template, request, jsonify
import os, threading, subprocess, config
from cortar import ejecutar_corte
from enviar import encolar_video

app = Flask(__name__)

# Asegurar carpetas de trabajo
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.PORTADA_FOLDER, exist_ok=True)

def flujo_produccion(ruta_v, ruta_p, nombre_s):
    print(f"\n[🚀] INICIANDO SISTEMA: {nombre_s}")
    
    try:
        # Medir duración del video
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{ruta_v}\""
        duracion = float(subprocess.check_output(cmd, shell=True))
        total_partes = int(duracion // 60) + (1 if duracion % 60 > 0 else 0)
        print(f"[📊] Info: {duracion}s | Partes: {total_partes}")
    except Exception as e:
        print(f"[❌] Error de ffprobe: {e}")
        return

    for i in range(total_partes):
        inicio = i * 60
        n_parte = i + 1
        ruta_out = os.path.join(config.UPLOAD_FOLDER, f"p{n_parte}_{os.path.basename(ruta_v)}")
        
        print(f"[✂️] Cortando Parte {n_parte}/{total_partes}...")
        
        # Llamada al motor de corte pasándole la portada seleccionada
        caption = ejecutar_corte(ruta_v, ruta_out, inicio, n_parte, total_partes, nombre_s, ruta_p)
        
        # Enviar a la cola de Telegram
        encolar_video(ruta_out, caption)

    print(f"[✅] {nombre_s} procesada y encolada.\n")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_task():
    video = request.files.get("video")
    portada = request.files.get("portada")
    nombre = request.form.get("nombre", "Mally Series")

    if video and portada:
        # Guardar archivos temporales
        path_v = os.path.join(config.UPLOAD_FOLDER, video.filename)
        video.save(path_v)
        
        path_p = os.path.join(config.PORTADA_FOLDER, "temp_portada.jpg")
        portada.save(path_p)
        
        print(f"[📂] Recibido: {video.filename} + Portada")

        # Iniciar proceso en segundo plano
        threading.Thread(target=flujo_produccion, args=(path_v, path_p, nombre)).start()
        
        return jsonify({"message": "🚀 ¡Producción iniciada! Revisa la consola y Telegram."})

    return jsonify({"message": "❌ Error: Falta video o portada"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
