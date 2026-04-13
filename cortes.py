import subprocess
import config

def extraer_segmento(path_input, n):
    """Corte directo sin re-codificación para máxima sincronía"""
    inicio = (n - 1) * config.CLIP_DURATION
    path_output = f"{config.TEMP_FOLDER}/raw_{n}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(inicio),
        '-t', str(config.CLIP_DURATION),
        '-i', path_input,
        '-c', 'copy', # ⚡ VELOCIDAD PURA: Copia directa sin procesar
        '-avoid_negative_ts', '1',
        path_output
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return path_output
