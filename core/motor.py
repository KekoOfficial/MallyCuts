import subprocess
import os
import re  # Para el buscador de duración
from config import *
from core.logger import log

# 🧠 DETECCIÓN AUTOMÁTICA DE FFMPEG
try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_BIN = "ffmpeg"

# ==============================================
# 📏 OBTENER DURACIÓN (MÉTODO SEGURO)
# ==============================================
def get_duration(ruta_video):
    try:
        # Intento 1: Método limpio
        comando = [
            FFMPEG_BIN, "-i", ruta_video,
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        salida = resultado.stdout.strip()
        
        if salida:
            return float(salida)

        # Intento 2: Buscar manualmente
        comando = [FFMPEG_BIN, "-i", ruta_video]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", resultado.stderr)
        if match:
            h = int(match.group(1))
            m = int(match.group(2))
            s = float(match.group(3))
            return h * 3600 + m * 60 + s

        return 0
    except Exception as e:
        log.error(f"No se pudo leer duración: {str(e)}")
        return 0

# ==============================================
# ⚡ CREAR CORTE (ARREGLADO PARA TERMUX)
# ==============================================
def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    try:
        comando = [
            FFMPEG_BIN, "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            "-filter_complex",
            # ✅ ARREGLO CLAVE: Cambiamos (oh-h)/4 por un valor fijo 200
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[vid];"
            f"[vid]pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[bg];"
            f"[1:v]scale=w=400:h=-1[logo];"
            f"[bg][logo]overlay=(W-w)/2:200[outv]",
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-threads", THREADS,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            ruta_salida
        ]

        proceso = subprocess.run(comando, capture_output=True, timeout=TIMEOUT_FFMPEG)

        if proceso.returncode == 0 and os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 300000:
            log.info(f"✅ Parte {parte}/{total} generada correctamente")
            return (
                f"🎬 {titulo}\n"
                f"💎 CAPÍTULO: {parte} / {total}\n"
                f"✅ Contenido Verificado\n"
                f"🔗 @MallySeries"
            )
        else:
            if proceso.stderr:
                error_texto = proceso.stderr[-1000:] if len(proceso.stderr) > 1000 else proceso.stderr
                log.error(f"💥 Error FFmpeg Parte {parte}:\n{error_texto}")
            return None

    except subprocess.TimeoutExpired:
        log.error(f"⏱️ Tiempo agotado Parte {parte}")
        return None
    except Exception as e:
        log.error(f"💥 Error crítico Parte {parte}: {str(e)}")
        return None
