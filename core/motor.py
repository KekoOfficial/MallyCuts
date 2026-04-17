import subprocess
import os
import time
import config
from core.logger import mally_log

def obtener_info_video(ruta):
    """Extrae duración y metadatos técnicos para asegurar el corte."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", ruta
        ]
        resultado = subprocess.check_output(cmd).decode().strip()
        return float(resultado)
    except Exception as e:
        mally_log.error(f"Error analizando video {ruta}: {e}")
        return 0

def ejecutar_corte(video_in, video_out, inicio, portada, parte, total, titulo):
    """
    Motor de alto rendimiento con gestión de errores y optimización de recursos.
    """
    if not os.path.exists(video_in):
        mally_log.error(f"Archivo de entrada no encontrado: {video_in}")
        return None

    # Comando optimizado: Seek rápido + Reencode eficiente + Metadatos para streaming
    comando = [
        "ffmpeg", "-y",
        "-ss", str(inicio), "-t", "60",        # Seek rápido (antes del input)
        "-i", video_in,                        # Entrada 0: Video
        "-i", portada,                         # Entrada 1: Imagen
        "-filter_complex", 
        "[0:v][1:v]overlay=shortest=1:format=yuv420[v]", # Overlay seguro
        "-map", "[v]",                         # Usar el video con overlay
        "-map", "0:a?",                        # Mapear audio original (si existe)
        "-c:v", "libx264",
        "-preset", "ultrafast",                # Velocidad máxima en procesadores ARM
        "-crf", config.CRF_QUALITY,            # Calidad balanceada definida en config
        "-threads", "1",                       # Limitar a 1 hilo por proceso para no colapsar RAM
        "-c:a", "aac", "-b:a", "96k", "-ac", "1", # Audio mono ligero para ahorrar peso
        "-movflags", "+faststart",             # Permite reproducción instantánea en Telegram
        video_out
    ]

    mally_log.info(f"🎞️ Procesando: Parte {parte}/{total} de '{titulo}'")
    
    intentos = 0
    max_intentos = 2
    
    while intentos < max_intentos:
        try:
            # Ejecutar proceso con tiempo límite para evitar bloqueos infinitos
            subprocess.run(
                comando, 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                timeout=config.TIMEOUT_FFMPEG
            )
            
            # Verificar si el archivo resultante es válido (mínimo 10KB)
            if os.path.exists(video_out) and os.path.getsize(video_out) > 10240:
                mally_log.info(f"✅ Corte exitoso: Parte {parte}")
                return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
            else:
                raise Exception("Archivo generado corrupto o demasiado pequeño.")

        except subprocess.TimeoutExpired:
            mally_log.error(f"⚠️ Timeout en parte {parte}. Reintentando...")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Error desconocido"
            mally_log.error(f"❌ Error FFmpeg en parte {parte}: {error_msg}")
        except Exception as e:
            mally_log.error(f"❌ Error inesperado en motor: {e}")

        intentos += 1
        time.sleep(2) # Pausa de seguridad antes de reintentar

    return None
