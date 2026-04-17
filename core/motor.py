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
    """Corta y superpone portada con calidad máxima"""
    try:
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            "-filter_complex",
            f"[0:v]scale={RESOLUCION}[vid];[1:v]scale=w=iw*min(1920/iw\\,1080/ih):h=ih*min(1920/iw\\,1080/ih)[img];[vid][img]overlay=shortest=1:format=yuv420[v]",
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", CODEC_VIDEO,
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-c:a", CODEC_AUDIO,
            "-b:a", BITRATE_AUDIO,
            "-movflags", "+faststart",
            ruta_salida
        ]
        
        subprocess.run(
            comando,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=TIMEOUT_FFMPEG
        )
        
        if os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 50000:
            return f"🎬 {titulo}\n💎 PARTE {parte} DE {total}\n🔗 @MallySeries"
        else:
            log.error(f"Archivo generado está vacío o corrupto: {ruta_salida}")
            return None
            
    except subprocess.TimeoutExpired:
        log.error(f"⏰ Tiempo agotado en parte {parte}")
        return None
    except Exception as e:
        log.error(f"❌ Error en corte {parte}: {str(e)}")
        return None
