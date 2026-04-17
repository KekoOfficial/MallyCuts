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
            ruta_entrada
        ]
        salida = subprocess.check_output(comando).decode().strip()
        return float(salida) if salida else 0
    except Exception as e:
        log.error(f"No se pudo leer duración: {e}")
        return 0

def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    """✅ MODO FORZADO: TODO VERTICAL 1080x1920 | TEXTO PERSONALIZADO"""
    try:
        comando = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            # 🚀 FORMATO VERTICAL FORZADO
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[vid];"
            f"[vid]pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[bg];"
            f"[1:v]scale=w=400:h=-1[logo];"
            f"[bg][logo]overlay=(W-w)/2:30[outv]",
            # CONFIGURACIÓN SEGURA
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
            
            # 📝 TEXTO EXACTO QUE PEDISTE
            return (
                f"🎬 {titulo}\n"
                f"💎 CAPÍTULO: {parte} / {total}\n"
                f"✅ Contenido Verificado\n"
                f"🔗 @MallySeries"
            )
        else:
            log.error(f"❌ Archivo vacío o muy pequeño: {ruta_salida}")
            return None

    except subprocess.CalledProcessError as e:
        log.error(f"💥 Error FFmpeg Parte {parte}: {e.stderr.decode()}")
        return None
    except Exception as e:
        log.error(f"❌ Error general Parte {parte}: {str(e)}")
        return None
