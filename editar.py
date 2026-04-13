import subprocess
import os
import config

def procesar_clip(path_input, n):
    """Aplica únicamente la cadena de filtros 4K, Audio y Marca de Agua"""
    
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)
        
    path_output = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
    
    # --- CONFIGURACIÓN DE FILTROS (SIN ESPACIOS) ---
    # Posicionamiento TikTok
    x_pos = "if(lt(mod(t,10),5),40,w-tw-40)"
    y_pos = "if(lt(mod(t,10),5),40,h-th-40)"
    
    # Cadena de Video: Escala + Nitidez + Color + Marca
    v_filter = (
        f"scale=1280:-2,"
        f"unsharp=3:3:0.7:3:3:0.0,"
        f"eq=contrast=1.1:saturation=1.2,"
        f"drawtext=text='{config.WATERMARK_TEXT}':x={x_pos}:y={y_pos}:"
        f"fontcolor=white@0.5:fontsize=28:shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )
    
    # Cadena de Audio: Compresión + Volumen
    a_filter = "acompressor=threshold=-20dB:ratio=4,volume=1.5"

    cmd = [
        'ffmpeg', '-y', 
        '-i', str(path_input),
        '-vf', v_filter,
        '-af', a_filter,
        '-c:v', 'libx264', 
        '-preset', 'ultrafast', 
        '-crf', '24',
        '-c:a', 'aac', 
        '-b:a', '128k',
        str(path_output)
    ]
    
    # Ejecución directa
    subprocess.run(cmd, check=True, capture_output=True)
    
    return path_output
