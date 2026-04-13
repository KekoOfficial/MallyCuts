import subprocess
import os
import config

def procesar_clip(path_input, n):
    """Cerebro de edición con blindaje de fuentes, escapes de texto y fallback de filtros"""
    
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)
        
    path_output = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
    
    # ✅ ERROR 1: Escapar texto de la marca de agua (Anti-Crash)
    safe_text = config.WATERMARK_TEXT.replace("'", "\\'").replace(":", "\\:")
    
    # ✅ ERROR 3: Verificación de ruta de fuente (Fallback de sistema)
    font_path = "/system/fonts/Roboto-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "/system/fonts/DroidSans.ttf" # Fallback común en Android
    
    # ✅ ERROR 2: Coordenadas con escape de comas (Imprescindible en Python/FFmpeg)
    x_pos = "if(lt(mod(t\\,10)\\,5)\\,40\\,w-tw-40)"
    y_pos = "if(lt(mod(t\\,10)\\,5)\\,40\\,h-th-40)"
    
    # Construcción de filtro de video (Sin unsharp para estabilidad total)
    v_filter = (
        f"scale=1280:-2,"
        f"eq=contrast=1.15:saturation=1.25," # Potenciamos color sin riesgo de crash
        f"drawtext=fontfile={font_path}:"
        f"text='{safe_text}':"
        f"x={x_pos}:y={y_pos}:"
        f"fontcolor=white@0.5:fontsize=28:shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )
    
    # ✅ ERROR 4: Audio simplificado para evitar errores de parseo de dB
    a_filter = "volume=1.5"

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
    
    # Ejecución con log de errores real
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n--- ⚠️ FALLO CRÍTICO EN PRODUCCIÓN ---")
        print(result.stderr) 
        raise subprocess.CalledProcessError(result.returncode, cmd)
        
    return path_output
