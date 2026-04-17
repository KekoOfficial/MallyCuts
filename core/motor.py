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
    """✅ VERSION ULTRA OPTIMIZADA: DETECTA VERTICAL / HORIZONTAL AUTOMÁTICAMENTE"""
    try:
        # 🔍 PRIMERO DETECTAMOS LA RESOLUCIÓN ORIGINAL
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0",
            ruta_entrada
        ]
        res = subprocess.check_output(probe_cmd).decode().strip()
        w, h = map(int, res.split('x'))

        # 🧠 DECIDIMOS FORMATO FINAL
        if h > w:  # ES VERTICAL
            RES_FINAL = "1080:1920"
            escala_video = f"scale=w=1080:h=1920:force_original_aspect_ratio=decrease[vid];[vid]pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[bg]"
            escala_logo = "scale=w=400:h=-1[logo]"
            posicion_logo = "overlay=(W-w)/2:30[outv]"
        else:      # ES HORIZONTAL
            RES_FINAL = "1920:1080"
            escala_video = f"scale=w=1920:h=1080:force_original_aspect_ratio=decrease[vid];[vid]pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black[bg]"
            escala_logo = "scale=w=350:h=-1[logo]"
            posicion_logo = "overlay=(W-w)/2:20[outv]"

        # 🚀 COMANDO FINAL
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            "-filter_complex",
            f"{escala_video};{escala_logo};[bg][logo]{posicion_logo}",
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
