import subprocess
import config

def aplicar_marca_agua(path_input, n):
    """Aplica el branding de Mally Series al clip extraído"""
    path_output = f"{config.TEMP_FOLDER}/cap_{n:03d}.mp4"
    
    comando = [
        'ffmpeg', '-y', '-i', path_input,
        '-vf', f"drawtext=text='{config.WATERMARK_TEXT}':x=w-tw-20:y=h-th-20:fontcolor={config.WATERMARK_COLOR}:fontsize=24",
        '-c:v', 'libx264', '-preset', 'superfast', '-crf', '28', 
        '-threads', '4', '-c:a', 'copy', path_output
    ]
    subprocess.run(comando, check=True, capture_output=True)
    return path_output
