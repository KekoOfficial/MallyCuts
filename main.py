from flask import Flask, render_template, request, jsonify
import os
import threading
import time
import traceback  # 🧠 Para ver errores completos
from config import *
from core.motor import get_duration, crear_corte
from core.enviar import enviar_a_telegram
from core.logger import log

# 🧠 DETECTAR AUTOMÁTICAMENTE EL ENTORNO
try:
    import imageio_ffmpeg
    FFMPEG_RUTA = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_RUTA
    log.info("☁️ Modo Render activado")
except ImportError:
    FFMPEG_RUTA = "ffmpeg"
    log.info("📱 Modo Local / Termux activado")

app = Flask(__name__, static_folder=STATIC_FOLDER)

# ==============================================
# 🚀 CONFIGURACIÓN PARA ARCHIVOS GIGANTES
# ==============================================
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10 GB
app.config['MAX_FORM_MEMORY_SIZE'] = 10 * 1024 * 1024 * 1024

# 🛡️ CONTROL DE CONCURRENCIA
PROCESO_ACTIVO = False

def proceso_completo(ruta_video, ruta_portada, titulo):
    """Función principal con logs detallados"""
    global PROCESO_ACTIVO
    try:
        log.info(f"🚀 INICIANDO PROCESO: {titulo}")

        duracion = get_duration(ruta_video)
        if duracion == 0:
            raise Exception("No se pudo leer la duración del video")

        total_partes = int(duracion // DURACION_POR_PARTE) + (1 if duracion % DURACION_POR_PARTE > 0 else 0)
        log.info(f"📊 Duración total: {round(duracion/60,2)} min | Partes: {total_partes}")

        for i in range(total_partes):
            numero = i + 1
            ruta_salida = os.path.join(UPLOAD_FOLDER, f"parte_{numero:03d}.mp4")

            log.info(f"✂️ Procesando parte {numero}/{total_partes}...")

            caption = crear_corte(
                ruta_video, ruta_salida, i * DURACION_POR_PARTE,
                ruta_portada, numero, total, titulo
            )

            if caption:
                log.info(f"📤 Enviando parte {numero} a Telegram...")
                if not enviar_a_telegram(ruta_salida, caption):
                    log.error("⛔ PROCESO DETENIDO: Falló el envío")
                    break
            else:
                log.error(f"❌ FALLÓ: No se pudo generar parte {numero}")

        log.info(f"🏁 FINALIZADO: {titulo}\n" + "="*50)

    except Exception as e:
        log.error(f"💥 ERROR CRÍTICO EN EL PROCESO: {str(e)}")
        log.error(f"🔍 RASTRO DEL ERROR:\n{traceback.format_exc()}")
    finally:
        # 🧹 LIMPIEZA SEGURA
        try:
            if os.path.exists(ruta_video): os.remove(ruta_video)
        except: pass
        try:
            if os.path.exists(ruta_portada): os.remove(ruta_portada)
        except: pass
        PROCESO_ACTIVO = False
        log.info("🔓 Sistema listo para nuevo trabajo")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    global PROCESO_ACTIVO
    try:
        # 🛡️ Verificar si está ocupado
        if PROCESO_ACTIVO:
            return jsonify({
                "status": "ocupado",
                "mensaje": "⏳ ESPERA... Hay un proceso activo."
            }), 429

        # 📥 Recibir datos
        if 'video' not in request.files or 'portada' not in request.files:
            raise Exception("Faltan archivos obligatorios (video o portada)")

        video = request.files['video']
        portada = request.files['portada']
        titulo = request.form.get('titulo', 'Sin Título')

        if video.filename == '':
            raise Exception("El archivo de video está vacío")

        # 📂 Guardar con nombres únicos
        timestamp = int(time.time())
        ruta_v = os.path.join(UPLOAD_FOLDER, f"original_{timestamp}.mp4")
        ruta_p = os.path.join(STATIC_FOLDER, f"portada_{timestamp}.jpg")

        video.save(ruta_v)
        portada.save(ruta_p)

        tamaño_mb = os.path.getsize(ruta_v) / (1024*1024)
        log.info(f"📥 ARCHIVO RECIBIDO: {tamaño_mb:.1f} MB")

        # 🔒 Marcar como ocupado
        PROCESO_ACTIVO = True

        # 🧵 Ejecutar en segundo plano
        hilo = threading.Thread(target=proceso_completo, args=(ruta_v, ruta_p, titulo), daemon=True)
        hilo.start()

        return jsonify({
            "status": "ok",
            "mensaje": f"🔥 PROCESO INICIADO!\nTítulo: {titulo}"
        })

    except Exception as e:
        log.error(f"⚠️ ERROR EN LA PETICIÓN: {str(e)}")
        log.error(f"🔍 DETALLE:\n{traceback.format_exc()}")
        PROCESO_ACTIVO = False
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# ==============================================
# 🚀 SERVIDOR FUERTE PARA TERMUX
# ==============================================
if __name__ == "__main__":
    log.info("⚔️ MALLYCUTS - MODO DIOS WEB ACTIVADO ⚔️")
    log.info(f"🔧 Configurado para: {'RENDER' if 'IMAGEIO_FFMPEG_EXE' in os.environ else 'TERMUX/PC'}")
    
    try:
        from waitress import serve
        log.info("⚡ Servidor WAITRESS activado (MÁS ESTABLE)")
        serve(app, host="0.0.0.0", port=5000, threads=10)
    except ImportError:
        log.info("🔧 Usando servidor normal")
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
