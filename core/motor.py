import subprocess
import os
from config import *
from core.logger import log

# 🧠 DETECCIÓN AUTOMÁTICA DE FFMPEG
try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_BIN = "ffmpeg"

def get_duration(ruta_video):
    """Obtiene duración del video"""
    try:
        comando = [
            FFMPEG_BIN, "-i", ruta_video,
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "default=noprint_wrappers=1:nokey=1"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        return float(resultado.stdout.strip())
    except Exception as e:
        log.error(f"❌ No se pudo leer duración: {str(e)}")
        return 0

def crear_corte(ruta_entrada, ruta_salida, inicio, ruta_portada, parte, total, titulo):
    """
    ⚡ MODO DIOS: Genera el corte vertical con portada
    """
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
            f"[bg][logo]overlay=(W-w)/2:(oh-h)/4:format=auto[outv]",
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

        # ==============================================
        # ▶️ EJECUTAR Y CAPTURAR TODO
        # ==============================================
        resultado = subprocess.run(
            comando,
            capture_output=True,
            timeout=TIMEOUT_FFMPEG
        )

        # ==============================================
        # ✅ VERIFICAR SI FUNCIONÓ
        # ==============================================
        if resultado.returncode == 0 and os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 300000:
            log.info(f"✅ Parte {parte}/{total} generada correctamente")
            return (
                f"🎬 {titulo}\n"
                f"💎 CAPÍTULO: {parte} / {total}\n"
                f"✅ Contenido Verificado\n"
                f"🔗 @MallySeries"
            )
        else:
            # ==============================================
            # ❌ MOSTRAR ERROR COMPLETO
            # ==============================================
            log.error(f"💥 FFMPEG FALLÓ EN PARTE {parte}")
            log.error(f"📝 Código de error: {resultado.returncode}")
            
            # Mostrar las últimas líneas del error real
            if resultado.stderr:
                # Tomamos los últimos 1500 caracteres para no llenar todo
                error_texto = resultado.stderr[-1500:] if len(resultado.stderr) > 1500 else resultado.stderr
                log.error(f"🔍 MENSAJE DE ERROR:\n{error_texto}")
            
            return None

    except subprocess.TimeoutExpired:
        log.error(f"⏱️ TIEMPO AGOTADO: Parte {parte} tardó demasiado")
        return None
    except Exception as e:
        log.error(f"💥 ERROR INESPERADO Parte {parte}: {str(e)}")
        return None
