import subprocess
import config

def extraer_segmento(path_original, n):
    """Extrae 60s sin procesar para pasar al cerebro de edición"""
    inicio = (n - 1) * config.CLIP_DURATION
    path_salida = f"{config.TEMP_FOLDER}/raw_{n}.mp4"
    
    cmd = [
        'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
        '-i', path_original, '-c', 'copy', '-avoid_negative_ts', 'make_zero', 
        path_salida
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path_salida
