import subprocess
import os
from config import *
from core.logger import log

# 🧠 SISTEMA INTELIGENTE: DETECTA AUTOMÁTICAMENTE EL ENTORNO
try:
    import imageio_ffmpeg
    # ✅ SI ESTAMOS EN RENDER: Usamos la ruta exacta
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    # ✅ SI ESTAMOS EN TERMUX O PC: Usamos el comando normal
    FFMPEG_BIN = "ffmpeg"

# ==============================================
# 📏 OBTENER DURACIÓN DEL VIDEO
# ==============================================
def get_duration(ruta_video):
    """Obtiene duración de forma eficiente"""
    try:
        comando = [
            FFMPEG_BIN, "-i", ruta_video,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "default=noprint_wrappers=1:nokey=1"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        return float(resultado.stdout.strip())
    except Exception as e:
        log.error(f"No se pudo leer duración: {str(e)}")
        return 0

# ==============================================
# ⚡ FUNCIÓN PRINCIPAL DE CORTE
# ==============================================
def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    """
    ⚡ MODO DIOS: VERTICAL 1080x1920
    - Auto-detección de velocidad
    - Mantiene calidad y pone portada
    """
    try:
        # ==============================================
        # 🚀 COMANDO PRINCIPAL CON TODO LO VISUAL
        # ==============================================
        comando = [
            FFMPEG_BIN, "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            
            # 📱 FILTRO COMPLEJO: ESCALAR + CENTRAR + PONER PORTADA
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[vid];"
            f"[vid]pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[bg];"
            f"[1:v]scale=w=400:h=-1[logo];"
            f"[bg][logo]overlay=(W-w)/2:(oh-h)/4:format=auto[outv]",
            
            # ⚡ SALIDA
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", PRESET,      # Usa la config rapida de config.py
            "-crf", CRF_QUALITY,
            "-threads", THREADS,   # Usa todos los núcleos
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            ruta_salida
        ]

        # ==============================================
        # ▶️ EJECUTAR PROCESO
        # ==============================================
        proceso = subprocess.run(
            comando,
            capture_output=True,
            timeout=TIMEOUT_FFMPEG
        )

        # ==============================================
        # ✅ VERIFICACIÓN DE ÉXITO
        # ==============================================
        if proceso.returncode == 0 and os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 300000:
            log.info(f"✅ Parte {parte}/{total} lista")
            return (
                f"🎬 {titulo}\n"
                f"💎 CAPÍTULO: {parte} / {total}\n"
                f"✅ Contenido Verificado\n"
                f"🔗 @MallySeries"
            )
        else:
            # Si falla, mostramos el error real para depurar
            if proceso.stderr:
                error_mensaje = proceso.stderr.decode('utf-8', errors='ignore')[-500:]
                log.error(f"💥 Detalle error FFmpeg: {error_mensaje}")
            log.error(f"❌ Falló generación de Parte {parte}")
            return None

    except subprocess.TimeoutExpired:
        log.error(f"⏱️ Tiempo agotado procesando Parte {parte}")
        return None
    except Exception as e:
        log.error(f"💥 Error crítico Parte {parte}: {str(e)}")
        return None
