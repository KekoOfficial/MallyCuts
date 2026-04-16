import subprocess
import config
import marcas

def extraer_segmento(path_input, n, aplicar_marca=False):
    """
    Corte sincronizado con protección anti-copyright.
    Se limpia el rastro de metadatos y se altera levemente el audio.
    """
    inicio = (n - 1) * config.CLIP_DURATION
    path_output = f"{config.TEMP_FOLDER}/cap_{n}.mp4"
    
    # Filtro de audio para alterar el pitch sutilmente (1.02x)
    # Esto ayuda a que el algoritmo no detecte la firma exacta del audio original.
    filtro_audio = "asetrate=44100*1.02,aresample=44100,atempo=1/1.02"

    if aplicar_marca:
        # Modo Procesado con Branding y Filtro Anti-Copyright
        filtro_video = marcas.obtener_filtro()
        cmd = [
            'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
            '-i', path_input, 
            '-vf', filtro_video,
            '-af', filtro_audio,      # 🛡️ Protección de audio
            '-map_metadata', '-1',     # 🧹 Limpia rastro de autor original
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            path_output
        ]
    else:
        # Modo Rápido con Limpieza de Metadatos y ligero re-encode de audio
        # Nota: Aquí no usamos '-c copy' para el audio porque necesitamos alterarlo.
        cmd = [
            'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
            '-i', path_input,
            '-af', filtro_audio,      # 🛡️ Protección de audio
            '-map_metadata', '-1',     # 🧹 Limpia rastro de autor original
            '-c:v', 'copy',            # Video rápido sin procesar
            '-c:a', 'aac',             # Re-encode de audio necesario para el filtro
            '-avoid_negative_ts', '1',
            path_output
        ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return path_output
