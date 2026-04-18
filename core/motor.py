import subprocess
import os
import imageio_ffmpeg
from config import *
from core.logger import log

# 📍 RUTA EXACTA DE FFMPEG
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

def get_duration(ruta_video):
    """Obtiene duración usando el MISMO ffmpeg, sin necesitar ffprobe"""
    try:
        comando = [
            FFMPEG_BIN, "-i", ruta_video
        ]
        # Corremos y capturamos la salida de error donde viene la duración
        resultado = subprocess.run(comando, capture_output=True, text=True)
        salida = resultado.stderr  # En ffmpeg la info sale por aquí
        
        # Buscamos la línea que dice "Duration"
        for linea in salida.split('\n'):
            if 'Duration' in linea:
                tiempo = linea.split(',')[0].split('Duration:')[1].strip()
                h, m, s = tiempo.split(':')
                total_segundos = int(h)*3600 + int(m)*60 + float(s)
                return total_segundos
        return 0
    except Exception as e:
        log.error(f"No se pudo leer duración: {e}")
        return 0

def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    try:
        comando = [
            FFMPEG_BIN, "-y",
            "-ss", str(inicio),
            "-t", str(DURACION_POR_PARTE),
            "-i", ruta_entrada,
            "-i", ruta_portada,
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[vid];"
            f"[vid]pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[bg];"
            f"[1:v]scale=w=400:h=-1[logo];"
            f"[bg][logo]overlay=(W-w)/2:30[outv]",
            "-map", "[outv]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-preset", PRESET,
            "-crf", CRF_QUALITY,
            "-threads", "4",
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
            stderr=subprocess.DEVNULL,
            timeout=TIMEOUT_FFMPEG
        )

        if os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 300000:
            log.info(f"✅ Parte {parte} generada correctamente")
            return (
                f"🎬 {titulo}\n"
                f"💎 CAPÍTULO: {parte} / {total}\n"
                f"✅ Contenido Verificado\n"
                f"🔗 @MallySeries"
            )
        else:
            log.error(f"❌ Archivo vacío o muy pequeño")
            return None

    except Exception as e:
        log.error(f"💥 Error: {str(e)}")
        return None
