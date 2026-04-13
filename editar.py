import subprocess
import config

def procesar_clip(path_input, n):
    """Procesamiento Cinematográfico Optimizado para Termux"""
    path_output = f"{config.TEMP_FOLDER}/cap_{n:03d}.mp4"
    
    # Lógica de posición (Marca TikTok)
    x_pos = "if(lt(mod(t,10),5), 40, w-tw-40)"
    y_pos = "if(lt(mod(t,10),5), 40, h-th-40)"
    
    # FILTROS DE VIDEO: Reducimos un poco el escalado para estabilidad
    video_filters = (
        "scale=1280:-2," # Bajamos a 720p (HD) si 1080p da error, o mantén 1920 si prefieres probar
        "unsharp=3:3:0.7:3:3:0.0," # Nitidez más ligera pero efectiva
        "eq=contrast=1.1:saturation=1.2," 
        f"drawtext=text='{config.WATERMARK_TEXT}':"
        f"x={x_pos}:y={y_pos}:"
        f"fontcolor=white@0.5:fontsize=28:" # Tamaño más estándar
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )

    # FILTRO DE AUDIO: Versión ligera (Sin loudnorm que causa crashes)
    audio_filters = "acompressor=threshold=-20dB:ratio=4,volume=1.5"

    cmd = [
        'ffmpeg', '-y', 
        '-i', path_input,
        '-vf', video_filters,
        '-af', audio_filters,
        '-c:v', 'libx264', 
        '-preset', 'ultrafast', # MÁXIMA VELOCIDAD para evitar Status 234
        '-crf', '24',           # Equilibrio entre peso y calidad
        '-c:a', 'aac', 
        '-b:a', '128k', 
        '-strict', '-2',        # Compatibilidad extra
        path_output
    ]
    
    # Capturamos el error para ver qué dice exactamente si vuelve a fallar
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg Error log: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
        
    return path_output
