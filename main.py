from flask import Flask, render_template, request, jsonify
import os
import threading
import time
from config import *
from core.motor import get_duration, crear_corte
from core.enviar import enviar_a_telegram
from core.logger import log

# 🧠 SISTEMA INTELIGENTE: DETECTA AUTOMÁTICAMENTE DÓNDE ESTÁ CORRIENDO
try:
    import imageio_ffmpeg
    # ✅ SI ESTAMOS EN RENDER: Usamos la ruta exacta
    FFMPEG_RUTA = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_RUTA
    log.info("☁️ Modo Render activado")
except ImportError:
    # ✅ SI ESTAMOS EN TERMUX O PC: Usamos el comando normal
    FFMPEG_RUTA = "ffmpeg"
    log.info("📱 Modo Local / Termux activado")

app = Flask(__name__, static_folder=STATIC_FOLDER)

def proceso_completo(ruta_video, ruta_portada, titulo):
    log.info(f"🚀 INICIANDO: {titulo}")

    duracion = get_duration(ruta_video)
    if duracion == 0:
        log.error("❌ Video inválido o corrupto")
        return

    total_partes = int(duracion // DURACION_POR_PARTE) + (1 if duracion % DURACION_POR_PARTE > 0 else 0)
    log.info(f"📊 Duración: {round(duracion/60,2)} min | Partes: {total_partes}")

    for i in range(total_partes):
        numero = i + 1
        ruta_salida = os.path.join(UPLOAD_FOLDER, f"parte_{numero:03d}.mp4")

        log.info(f"✂️ Procesando parte {numero}/{total_partes}...")

        caption = crear_corte(
            ruta_video,
            ruta_salida,
            inicio = i * DURACION_POR_PARTE,
            ruta_portada = ruta_portada,
            parte = numero,
            total = total_partes,
            titulo = titulo
        )

        if caption:
            if not enviar_a_telegram(ruta_salida, caption):
                log.error("⛔ Proceso detenido por fallos consecutivos")
                break
        else:
            log.error(f"❌ No se pudo generar parte {numero}")

    # 🧹 Limpieza final automática
    if os.path.exists(ruta_video): os.remove(ruta_video)
    if os.path.exists(ruta_portada): os.remove(ruta_portada)

    log.info(f"🏁 FINALIZADO: {titulo}\n" + "="*45)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    try:
        video = request.files['video']
        portada = request.files['portada']
        titulo = request.form.get('titulo', 'Sin Título')

        # Guardar archivos temporales con nombre único
        ruta_v = os.path.join(UPLOAD_FOLDER, f"original_{int(time.time())}.mp4")
        ruta_p = os.path.join(STATIC_FOLDER, "portada_temp.jpg")

        video.save(ruta_v)
        portada.save(ruta_p)

        # Ejecutar en segundo plano para no congelar la web
        hilo = threading.Thread(target=proceso_completo, args=(ruta_v, ruta_p, titulo), daemon=True)
        hilo.start()

        return jsonify({
            "status": "ok",
            "mensaje": f"🔥 Proceso iniciado!\nTítulo: {titulo}"
        })

    except Exception as e:
        log.error(f"⚠️ Error en formulario: {e}")
        return jsonify({"status": "error", "mensaje": str(e)})

if __name__ == "__main__":
    log.info("⚔️ MALLYCUTS - MODO DIOS ACTIVADO ⚔️")
    log.info(f"🔧 Configurado para: {'RENDER' if 'IMAGEIO_FFMPEG_EXE' in os.environ else 'TERMUX/PC'}")
    app.run(host="0.0.0.0", port=5000, debug=False)
