import subprocess
import config

def extraer_segmento(path_original, n):
    """Corta el segmento de 60 segundos exactos"""
    inicio = (n - 1) * config.CLIP_DURATION
    path_salida = f"{config.TEMP_FOLDER}/raw_{n}.mp4"
    
    comando = [
        'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
        '-i', path_original, '-c', 'copy', '-avoid_negative_ts', '1', path_salida
    ]
    subprocess.run(comando, check=True, capture_output=True)
    return path_salida
