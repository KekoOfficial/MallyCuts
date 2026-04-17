from flask import Flask, render_template, request, jsonify
import os
import threading
import config
from core.motor import ejecutar_corte, obtener_info_video
from core.enviar import subir_a_telegram
from core.logger import mally_log

app = Flask(__name__)

# Asegurar limpieza de carpetas al iniciar
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.PORTADA_FOLDER, exist_ok=True)

def flujo_produccion_secuencial(path_v, path_p, nombre):
    """
    Sistema de producción lineal: 
    Corta Parte N -> Envía Parte N -> Elimina Parte N -> Siguiente.
    """
    mally_log.info(f"🚀 INICIANDO PRODUCCIÓN 1-A-1: {nombre}")
    
    duracion = obtener_info_video(path_v)
    if duracion == 0:
        mally_log.error("❌ Abortado: No se pudo leer la duración del video.")
        return

    total_partes = int(duracion // 60) + (1 if duracion % 60 > 0 else 0)
    mally_log.info(f"📊 Total a procesar: {total_partes} partes.")

    for i in range(total_partes):
        n_parte = i + 1
        inicio = i * 60
        # Nombre temporal único para la parte actual
        ruta_out = os.path.join(config.UPLOAD_FOLDER, f"temp_parte_{n_parte}.mp4")

        # --- FASE 1: CORTE ---
        mally_log.info(f"🎬 [Fase 1/2] Cortando parte {n_parte}/{total_partes}...")
        caption = ejecutar_corte(
            path_v, ruta_out, inicio, path_p, 
            n_parte, total_partes, nombre
        )

        if caption:
            # --- FASE 2: ENVÍO ---
            mally_log.info(f"📤 [Fase 2/2] Enviando parte {n_parte} a Telegram...")
            # Aquí el sistema se detiene y espera la respuesta de Telegram
            exito = subir_a_telegram(ruta_out, caption)
            
            if exito:
                mally_log.info(f"✅ Parte {n_parte} enviada y liberada de memoria.")
            else:
                mally_log.error(f"❌ Error crítico de envío en parte {n_parte}. Deteniendo flujo.")
                break # Detiene la serie si hay un error de red insalvable
        else:
            mally_log.error(f"❌ Falló el corte de la parte {n_parte}. Saltando a la siguiente...")

    mally_log.info(f"🏁 SERIE FINALIZADA: {nombre}")
    
    # Limpieza del video original para liberar espacio en el móvil
    if os.path.exists(path_v):
        try:
            os.remove(path_v)
            mally_log.info("🧹 Video original eliminado del servidor.")
        except: pass

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_task():
    video = request.files.get("video")
    portada = request.files.get("portada")
    nombre = request.form.get("nombre", "Mally Series")

    if video and portada:
        path_v = os.path.join(config.UPLOAD_FOLDER, video.filename)
        path_p = os.path.join(config.PORTADA_FOLDER, "temp_portada.jpg")
        
        video.save(path_v)
        portada.save(path_p)

        mally_log.info(f"[📂] Video recibido: {video.filename}")

        # Lanzar la línea de producción en un hilo separado para no bloquear la web
        threading.Thread(
            target=flujo_produccion_secuencial, 
            args=(path_v, path_p, nombre), 
            daemon=True
        ).start()

        return jsonify({"message": "🚀 Producción 1-a-1 iniciada correctamente."})

    return jsonify({"error": "Faltan archivos requeridos"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
