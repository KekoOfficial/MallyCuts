from flask import Flask, render_template, request, jsonify
import os
import threading
import time
from config import *
from core.motor import get_duration, crear_corte
from core.enviar import enviar_a_telegram
from core.logger import log

# 🧠 DETECTAR AUTOMÁTICAMENTE DÓNDE ESTAMOS CORRIENDO
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
# ⚙️ CONFIGURACIÓN SEGURA
# ==============================================
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB Límite realista
app.url_map.strict_slashes = False

# 🛡️ CONTROL DE CONCURRENCIA
PROCESO_ACTIVO = False
COLA_TAREAS = []

def proceso_completo(ruta_video, ruta_portada, titulo):
    """Función principal con manejo de recursos"""
    global PROCESO_ACTIVO
    
    try:
        log.info(f"🚀 INICIANDO: {titulo}")

        duracion = get_duration(ruta_video)
        if duracion == 0:
            raise Exception("Video inválido o corrupto")

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

        log.info(f"🏁 FINALIZADO: {titulo}\n" + "="*45)

    except Exception as e:
        log.error(f"💥 ERROR EN PROCESO: {str(e)}")
    finally:
        # 🧹 LIMPIEZA SEGURA
        try:
            if os.path.exists(ruta_video): os.remove(ruta_video)
        except: pass
        try:
            if os.path.exists(ruta_portada): os.remove(ruta_portada)
        except: pass
        
        PROCESO_ACTIVO = False
        log.info("🔓 Sistema libre para nueva tarea")

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
                "mensaje": "⏳ ESPERA... Hay un proceso activo.\nEl sistema procesa uno a la vez para no colapsar."
            }), 429

        # 📥 Recibir datos
        if 'video' not in request.files or 'portada' not in request.files:
            raise Exception("Faltan archivos obligatorios")

        video = request.files['video']
        portada = request.files['portada']
        titulo = request.form.get('titulo', 'Sin Título')

        if video.filename == '':
            raise Exception("Video vacío")

        # 📂 NOMBRES ÚNICOS PARA NO PISAR NADA
        timestamp = int(time.time())
        ruta_v = os.path.join(UPLOAD_FOLDER, f"original_{timestamp}.mp4")
        ruta_p = os.path.join(STATIC_FOLDER, f"portada_{timestamp}.jpg")

        video.save(ruta_v)
        portada.save(ruta_p)

        tamaño_mb = os.path.getsize(ruta_v) / (1024*1024)
        log.info(f"📥 Archivo recibido: {tamaño_mb:.1f} MB")

        # 🔒 Marcar como ocupado
        PROCESO_ACTIVO = True

        # 🧵 Ejecutar en segundo plano
        hilo = threading.Thread(target=proceso_completo, args=(ruta_v, ruta_p, titulo), daemon=True)
        hilo.start()

        return jsonify({
            "status": "ok",
            "mensaje": f"🔥 PROCESO INICIADO!\nTítulo: {titulo}\n✅ Modo Estable Activado"
        })

    except Exception as e:
        log.error(f"⚠️ ERROR: {str(e)}")
        PROCESO_ACTIVO = False
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == "__main__":
    log.info("⚔️ MALLYCUTS - MODO DIOS ESTABLE ⚔️")
    log.info(f"🔧 Configurado para: {'RENDER' if 'IMAGEIO_FFMPEG_EXE' in os.environ else 'TERMUX/PC'}")
    
    # 🚀 Servidor robusto
    try:
        from waitress import serve
        log.info("⚡ Servidor WAITRESS activado")
        serve(app, host="0.0.0.0", port=5000)
    except ImportError:
        log.info("🔧 Servidor Normal activado")
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
