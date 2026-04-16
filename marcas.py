import os
import sys
import subprocess
# Importa la infraestructura unificada y el logger
try:
    import config as cfg
    import logger
except ImportError:
    print("❌ Errormarcas: No se encontró config.py o logger.py.")
    sys.exit(1)

def aplicar_branding_ ffmpeg(video_path, output_path, start_time, duration, chapter):
    """
    DELEGADO: Aplica marca de agua inteligente y optimiza el video usando FFmpeg.
    Usa los parámetros de config.py.
    """
    logger.registrar_log(f"🎬 [FFMPEG CAP{chapter}] Iniciando renderizado FFmpeg optimizado para móvil...")
    
    # Filtro drawtext complejo para marca de agua con sombra
    filter_complex = (
        f"drawtext=text='{cfg.WATERMARK_TEXT}':x=10:y=H-th-10:"
        f"fontcolor={cfg.WATERMARK_COLOR}:fontsize={cfg.WATERMARK_SIZE}:"
        f"shadowcolor=black@{cfg.SHADOW_OPACITY}:shadowx=2:shadowy=2"
    )
    
    command = [
        'ffmpeg', '-y', # Sobrescribir si existe
        '-ss', str(start_time), # Tiempo de inicio del corte
        '-t', str(duration), # Duración del corte
        '-i', video_path,
        '-vf', filter_complex, # Aplicar filtro de branding
        '-c:v', cfg.VIDEO_CODEC,
        '-preset', cfg.PRESET_SPEED,
        '-crf', cfg.CRF_QUALITY,
        '-b:v', cfg.VIDEO_BITRATE,
        '-c:a', cfg.AUDIO_CODEC,
        '-b:a', cfg.AUDIO_BITRATE,
        output_path
    ]
    
    # Redirigir logs según cfg.DEBUG_MODE
    stdout_dest = subprocess.PIPE if cfg.DEBUG_MODE else subprocess.DEVNULL
    stderr_dest = subprocess.PIPE if cfg.DEBUG_MODE else subprocess.DEVNULL
    
    try:
        # Ejecuta FFmpeg usando subprocess
        process = subprocess.Popen(command, stdout=stdout_dest, stderr=stderr_dest, text=True)
        
        if cfg.DEBUG_MODE:
            # Si está en debug, imprimir la salida de FFmpeg en el log unificado
            for line in process.stderr:
                logger.registrar_log(f"[FFMPEG-DEBUG] {line.strip()}")
        
        process.wait() # Esperar a que FFmpeg termine el renderizado
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg falló con código {process.returncode}")
            
        logger.registrar_log(f"✅ [FFMPEG CAP{chapter}] Capítulo renderizado con éxito.")
        return True # Retorna True si el renderizado es exitoso

    except subprocess.CalledProcessError as e:
        logger.registrar_log(f"❌ [FFMPEG-ERROR] FFmpeg falló críticamente: {str(e)}")
        return False # Retorna False si falla
    except Exception as e:
        logger.registrar_log(f"❌ [FFMPEG-ERROR UNIFICADO] {str(e)}")
        return False # Retorna False si falla
