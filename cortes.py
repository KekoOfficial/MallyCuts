import subprocess
import config
import marcas

def extraer_segmento(path_input, n, aplicar_marca=False):
    """Corte sincronizado. 'copy' para velocidad, 'vf' para marca."""
    inicio = (n - 1) * config.CLIP_DURATION
    path_output = f"{config.TEMP_FOLDER}/cap_{n}.mp4"
    
    if aplicar_marca:
        # Modo Procesado (Más lento, con logo)
        cmd = [
            'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
            '-i', path_input, '-vf', marcas.obtener_filtro(),
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', path_output
        ]
    else:
        # Modo Express (Instantáneo)
        cmd = [
            'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
            '-i', path_input, '-c', 'copy', '-avoid_negative_ts', '1', path_output
        ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return path_output
