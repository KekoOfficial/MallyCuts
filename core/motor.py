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
    """Corta y superpone portada asegurando que haya video visible"""
    try:
        # COMANDO CORREGIDO: Asegura salida de video y formato compatible
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            "-filter_complex",
            f"[0:v]scale={RESOLUCION}:force_original_aspect_ratio=decrease,pad={RESOLUCION}:(ow-iw)/2:(oh-ih)/2,setsar=1[bg];"
            f"[1:v]scale=w=iw*min(1.0\\,ih*0.2/ih):h=ih*min(1.0\\,iw*0.2/iw)[logo];"
            f"[bg][logo]overlay=W-w-10:10:format=auto[v]",
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", CODEC_VIDEO,
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-pix_fmt", "yuv420p",
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
        
        # Verificar que el archivo tenga tamaño suficiente
        if os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 100000: # Mínimo 100KB
            return f"🎬 {titulo}\n💎 PARTE {parte} DE {total}\n🔗 @MallySeries"
        else:
            log.error(f"Archivo generado es demasiado pequeño o vacío: {ruta_salida}")
            return None
            
    except subprocess.TimeoutExpired:
        log.error(f"⏰ Tiempo agotado en parte {parte}")
        return None
    except Exception as e:
        log.error(f"❌ Error en corte {parte}: {str(e)}")
        return None
