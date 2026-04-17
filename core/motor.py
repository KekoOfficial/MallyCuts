import subprocess
import os
from config import *
from core.logger import log

def get_duration(ruta_video):
    """Obtiene duración total del video en segundos"""
    try:
        comando = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            ruta_video
        ]
        return float(subprocess.check_output(comando).decode().strip())
    except Exception as e:
        log.error(f"No se pudo leer duración: {e}")
        return 0

def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    """✅ VERSION FINAL: Se ve bien en VERTICAL y HORIZONTAL | REPRODUCE EN TELEGRAM"""
    try:
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            # FILTRO ADAPTATIVO
            "-filter_complex",
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase[vid];"
            f"[vid]crop=1920:1080:((iw-1920)/2):((ih-1080)/2)[bg];"
            f"[1:v]scale=w=350:h=-1[logo];"
            f"[bg][logo]overlay=(W-w)/2:20:format=yuv420[outv]",
            # CONFIGURACIÓN DE SALIDA
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            ruta_salida
        ]

        resultado = subprocess.run(
            comando,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_FFMPEG
        )

        if os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 300000:
            log.info(f"✅ Parte {parte} generada correctamente")
            return f"🎬 {titulo}\n💎 PARTE {parte} DE {total}\n🔗 @MallySeries"
        else:
            log.error(f"❌ Archivo vacío o muy pequeño: {ruta_salida}")
            return None

    except subprocess.CalledProcessError as e:
        log.error(f"💥 Error FFmpeg Parte {parte}: {e.stderr.decode()}")
        return None
    except Exception as e:
        log.error(f"❌ Error general Parte {parte}: {str(e)}")
        return None
