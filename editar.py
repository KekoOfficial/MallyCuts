import subprocess
import os
import config

def procesar_clip(path_input, n):
    """
    Cerebro de edición con VBR (Variable Bitrate) Controlado.
    Evita el error 413: Request Entity Too Large.
    """
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)
        
    path_output = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
    
    # --- LÓGICA DE SEGURIDAD (KHASAM PROTOCOL) ---
    safe_text = config.WATERMARK_TEXT.replace("'", "\\'").replace(":", "\\:")
    
    # Búsqueda de fuente disponible en Android
    font_path = "/system/fonts/Roboto-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/system/fonts/DroidSans.ttf"
    
    # Coordenadas con doble escape para el parser de FFmpeg
    x_pos = "if(lt(mod(t\\,10)\\,5)\\,40\\,w-tw-40)"
    y_pos = "if(lt(mod(t\\,10)\\,5)\\,40\\,h-th-40)"
    
    # Filtros: Reescalado, Mejora de Color y Marca de Agua
    v_filter = (
        f"scale=1280:-2,"
        f"eq=contrast=1.15:saturation=1.25," 
        f"drawtext=fontfile={font_path}:text='{safe_text}':"
        f"x={x_pos}:y={y_pos}:fontcolor=white@0.5:fontsize=28:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )

    # Comando con límite de Bitrate (Crucial para estabilidad)
    cmd = [
        'ffmpeg', '-y', 
        '-i', str(path_input),
        '-vf', v_filter,
        '-af', "volume=1.5",
        '-c:v', 'libx264', 
        '-preset', 'ultrafast', 
        '-crf', '26',           # Calidad balanceada
        '-maxrate', '3M',       # Límite de 3 Megabits por segundo (~22MB/min)
        '-bufsize', '6M',       # Tolerancia de picos
        '-c:a', 'aac', 
        '-b:a', '128k',
        str(path_output)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ Error FFmpeg en Cap {n}:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
        
    return path_output
