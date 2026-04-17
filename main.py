from flask import Flask, render_template, request, jsonify
import os, threading, config
from core.motor import ejecutar_corte
from core.enviar import encolar_para_telegram
from concurrent.futures import ProcessPoolExecutor

app = Flask(__name__)
# El executor se inicializa en el bloque main
executor = None

def flujo_maestro(path_v, path_p, nombre):
    """Organiza la producción sin bloquear el servidor."""
    # 1. Obtener duración (usar ffprobe aquí si es necesario)
    total_partes = 134 # Ejemplo para tu video actual
    
    print(f"[⚙️] Iniciando producción paralela: {nombre}")
    
    futures = []
    for i in range(total_partes):
        inicio = i * 60
        n_parte = i + 1
        ruta_out = os.path.join(config.UPLOAD_FOLDER, f"p{n_parte}_{os.path.basename(path_v)}")
        
        # Enviar al pool de procesos
        f = executor.submit(ejecutar_corte, path_v, ruta_out, inicio, path_p, n_parte, total_partes, nombre)
        f.add_done_callback(lambda future, r=ruta_out, p=n_parte: encolar_para_telegram(r, future.result(), p))
        futures.append(f)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    video = request.files['video']
    portada = request.files['portada']
    nombre = request.form.get('nombre', 'Mally Series')
    
    path_v = os.path.join(config.UPLOAD_FOLDER, video.filename)
    path_p = os.path.join(config.PORTADA_FOLDER, "current_portada.jpg")
    video.save(path_v)
    portada.save(path_p)
    
    threading.Thread(target=flujo_maestro, args=(path_v, path_p, nombre), daemon=True).start()
    return jsonify({"message": "Producción iniciada en Segundo Plano"})

if __name__ == "__main__":
    executor = ProcessPoolExecutor(max_workers=config.MAX_WORKERS)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
