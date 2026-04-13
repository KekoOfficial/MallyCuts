import subprocess
import config

def extraer_segmento(path_original, n):
    inicio = (n - 1) * config.CLIP_DURATION
    path_salida = f"{config.TEMP_FOLDER}/raw_{n}.mp4"
    
    # Usamos -accurate_seek para que el corte sea perfecto en el segundo indicado
    cmd = [
        'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
        '-i', path_original, '-c', 'copy', '-avoid_negative_ts', 'make_zero', 
        path_salida
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path_salida
