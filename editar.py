import subprocess
import config

def procesar_clip(path_input, n):
    """Aplica Filtro 4K, Audio Normalizado y Marca de Agua TikTok"""
    path_output = f"{config.TEMP_FOLDER}/cap_{n:03d}.mp4"
    
    # Lógica de posición TikTok (Salto cada 5 seg)
    x_pos = "if(lt(mod(t,10),5), 40, w-tw-40)"
    y_pos = "if(lt(mod(t,10),5), 40, h-th-40)"
    
    # Filtros: Escalado + Nitidez (4K Look) + Color + Marca de Agua
    video_filters = (
        "scale=1920:-2, " 
        "unsharp=5:5:0.8:5:5:0.0, " # Nitidez de bordes
        "eq=contrast=1.15:saturation=1.3:brightness=0.02, " # Mejora de color
        f"drawtext=text='{config.WATERMARK_TEXT}':"
        f"x={x_pos}:y={y_pos}:"
        f"fontcolor={config.WATERMARK_COLOR}:"
        f"fontsize={config.WATERMARK_SIZE}:"
        f"shadowcolor=black@0.6:shadowx=3:shadowy=3"
    )

    # Filtros: Compresor de audio + Normalización de volumen
    audio_filters = "acompressor=threshold=-20dB:ratio=4,loudnorm=I=-16:TP=-1.5"

    cmd = [
        'ffmpeg', '-y', '-i', path_input,
        '-vf', video_filters,
        '-af', audio_filters,
        '-c:v', 'libx264', 
        '-preset', 'superfast', 
        '-crf', '20', # Calidad alta
        '-threads', '0', 
        '-c:a', 'aac', '-b:a', '160k', 
        path_output
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return path_output
