import subprocess
import config

def aplicar_marca_agua(path_input, n):
    path_output = f"{config.TEMP_FOLDER}/cap_{n:03d}.mp4"
    
    # Fórmulas de centrado: (w-tw)/2 y (h-th)/2
    filtro = (f"drawtext=text='{config.WATERMARK_TEXT}':"
              f"x=(w-tw)/2:y=(h-th)/2:"
              f"fontcolor={config.WATERMARK_COLOR}:"
              f"fontsize={config.WATERMARK_SIZE}")
    
    cmd = [
        'ffmpeg', '-y', '-i', path_input,
        '-vf', filtro,
        '-c:v', 'libx264', '-preset', 'superfast', '-crf', '26', 
        '-threads', '0', # '0' usa todos los núcleos disponibles automáticamente
        '-c:a', 'copy', path_output
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path_output
