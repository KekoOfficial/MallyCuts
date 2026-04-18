import subprocess
import config
import os

def extraer_segmento(path_input, n):
    inicio = (n - 1) * config.CLIP_DURATION
    path_output = f"{config.TEMP_FOLDER}/parte_{n}.mp4"
    
    # 🔥 MODO VERTICAL 1080x1920
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(inicio),
        '-i', path_input,
        '-t', str(config.CLIP_DURATION),
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        path_output
    ]
    
    subprocess.run(cmd, capture_output=True)
    return path_output
