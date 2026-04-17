from flask import Flask, render_template, request, jsonify
import os
import threading
import subprocess
import config

from cortar import ejecutar_corte
from enviar import encolar_video
from concurrent.futures import ProcessPoolExecutor

app = Flask(__name__)

# Asegurar directorios
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.PORTADA_FOLDER, exist_ok=True)

# El ejecutor se define globalmente pero se inicializa en el bloque principal
executor = None

def obtener_duracion(ruta_v):
    """Calcula la duración exacta del video usando ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                ruta_v
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[❌] Error obteniendo duración: {e}")
        return 0

def procesar_parte(ruta_v, ruta_p, nombre_s, inicio, n_parte, total_partes):
    """Esta función corre en un proceso independiente para cada clip."""
    try:
        ruta_out = os.path.join(
            config.UPLOAD_FOLDER,
            f"p{n_parte}_{os.path.basename(ruta_v)}"
        )

        # Ejecutar el motor de corte (FFmpeg)
        caption = ejecutar_corte(
            ruta_v,
            ruta_out,
            inicio,
            n_parte,
            total_partes,
            nombre_s,
            ruta_p
        )

        # Enviar a la cola de Telegram (enviar.py gestionará el orden)
        encolar_video(ruta_out, caption, n_parte)

    except Exception as e:
        print(f"[💀] Error crítico en parte {n_parte}: {e}")

def flujo_produccion(ruta_v, ruta_p, nombre_s):
    """Hilo maestro que organiza la cola de procesos paralelos."""
    print(f"\n[🚀] INICIANDO SISTEMA: {nombre_s}")

    duracion = obtener_duracion(ruta_v)
    if duracion == 0:
        print("[❌] Cancelado: No se pudo leer el archivo de video.")
        return

    total_partes = int(duracion // 60) + (1 if duracion % 60 > 0 else 0)
    print(f"[📊] Total: {duracion:.2f}s | Partes a generar: {total_partes}")

    futures = []
    # Lanzamos los cortes al pool de procesos
    for i in range(total_partes):
        inicio = i * 60
        n_parte = i + 1

        print(f"[➕] Encolando Parte {n_parte}/{total_partes}")

        future = executor.submit(
            procesar_parte,
            ruta_v,
            ruta_p,
            nombre_s,
            inicio,
            n_parte,
            total_partes
        )
        futures.append(future)

    # Esperar a que todos los procesos terminen para dar el aviso final
    for f in futures:
        try:
            f.result()
        except Exception as e:
            print(f"[⚠️] Un proceso de corte falló: {e}")

    print(f"\n[✅] PRODUCCIÓN FINALIZADA: {nombre_s}")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_task():
    video = request.files.get("video")
    portada = request.files.get("portada")
    nombre = request.form.get("nombre", "Mally Series")

    if video and portada:
        path_v = os.path.join(config.UPLOAD_FOLDER, video.filename)
        video.save(path_v)

        # Guardar portada con nombre fijo para facilitar acceso
        path_p = os.path.join(config.PORTADA_FOLDER, "temp_portada.jpg")
        portada.save(path_p)

        print(f"[📂] Archivos recibidos: {video.filename}")

        # Lanzar el flujo en un hilo separado para no bloquear el navegador
        threading.Thread(
            target=flujo_produccion,
            args=(path_v, path_p, nombre),
            daemon=True
        ).start()

        return jsonify({
            "status": "success",
            "message": "🚀 ¡Producción Mally iniciada!",
            "info": f"Procesando {nombre} en paralelo ({config.MAX_WORKERS} núcleos)"
        })

    return jsonify({"error": "Falta subir el video o la portada"}), 400

if __name__ == "__main__":
    # Inicialización segura para Multiprocessing en Android/Termux
    executor = ProcessPoolExecutor(max_workers=config.MAX_WORKERS)
    
    print(f"🔥 Mally Cuts Pro corriendo en puerto 5000...")
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
