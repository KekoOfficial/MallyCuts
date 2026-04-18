import os
import time
from config import *
from core.motor import get_duration, crear_corte
from core.enviar import enviar_a_telegram
from core.logger import log

# ==============================================
# ⚙️ CONFIGURACIÓN MANUAL
# ==============================================
NOMBRE_ARCHIVO_VIDEO = "1000547702.mp4"  # 📝 Pon el nombre exacto de tu video
NOMBRE_ARCHIVO_IMAGEN = "1000550662.png" # 📝 Pon el nombre exacto de tu imagen
TITULO = "La chica buena se cansó"        # 📝 Pon el título que quieras

# ==============================================
# 🚀 INICIO DEL PROCESO
# ==============================================
if __name__ == "__main__":
    log.info("="*60)
    log.info("⚔️  MODO DIRECTO ACTIVADO - SIN NAVEGADOR ⚔️")
    log.info("="*60)

    # Rutas completas
    ruta_video = os.path.join(UPLOAD_FOLDER, NOMBRE_ARCHIVO_VIDEO)
    ruta_portada = os.path.join(STATIC_FOLDER, NOMBRE_ARCHIVO_IMAGEN)

    # Verificar que existan
    if not os.path.exists(ruta_video):
        log.error(f"❌ NO ENCONTRADO: {ruta_video}")
        exit()
    if not os.path.exists(ruta_portada):
        log.error(f"❌ NO ENCONTRADO: {ruta_portada}")
        exit()

    log.info(f"📹 Video: {NOMBRE_ARCHIVO_VIDEO}")
    log.info(f"🖼️ Portada: {NOMBRE_ARCHIVO_IMAGEN}")
    log.info(f"📝 Título: {TITULO}")

    # Obtener duración
    duracion = get_duration(ruta_video)
    if duracion == 0:
        log.error("❌ No se pudo leer el video")
        exit()

    total_partes = int(duracion // DURACION_POR_PARTE) + (1 if duracion % DURACION_POR_PARTE > 0 else 0)
    log.info(f"📊 Duración: {round(duracion/60,2)} min | Partes: {total_partes}")
    log.info("🚀 INICIANDO CORTE Y ENVÍO...")

    # Bucle principal
    for i in range(total_partes):
        numero = i + 1
        ruta_salida = os.path.join(UPLOAD_FOLDER, f"parte_{numero:03d}.mp4")

        log.info(f"✂️ Procesando parte {numero}/{total_partes}...")

        caption = crear_corte(
            ruta_entrada = ruta_video,
            ruta_salida = ruta_salida,
            inicio = i * DURACION_POR_PARTE,
            ruta_portada = ruta_portada,
            parte = numero,
            total = total_partes,
            titulo = TITULO
        )

        if caption:
            log.info(f"✅ Parte {numero} generada. Enviando...")
            if not enviar_a_telegram(ruta_salida, caption):
                log.error("⛔ Se detiene por error de envío")
                break
        else:
            log.error(f"❌ Falló al generar parte {numero}")

    # Limpieza final
    log.info("🏁 PROCESO FINALIZADO")
    log.info("="*60)
