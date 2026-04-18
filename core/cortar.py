import subprocess
import config
import os

def extraer_segmento(path_input, n):
    inicio = (n - 1) * config.CLIP_DURATION
    path_output = f"{config.TEMP_FOLDER}/parte_{n}.mp4"
    
    # ⚡ VELOCIDAD MAXIMA -c copy (Copia directa)
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(inicio),
        '-i', path_input,
        '-t', str(config.CLIP_DURATION),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        path_output
    ]
    
    subprocess.run(cmd, capture_output=True)
    return path_output
