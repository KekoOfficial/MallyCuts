import subprocess
import config
import re

def obtener_punto_silencio(path_original, inicio):
    """Analiza el audio cerca del segundo 60 para encontrar un vacío"""
    # Analizamos una ventana de 4 segundos (desde el 58 al 62)
    try:
        cmd = [
            'ffmpeg', '-ss', str(inicio + 58), '-t', '4',
            '-i', path_original,
            '-af', 'silencedetect=n=-30dB:d=0.05',
            '-f', 'null', '-'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        # Buscamos el primer silencio en esa ventana
        match = re.search(r"silence_start: ([\d.]+)", res.stderr)
        if match:
            # Calculamos el tiempo relativo al inicio del video original
            return float(match.group(1)) - inicio
    except:
        pass
    return config.CLIP_DURATION # Si falla, volvemos al estándar de 60s

def extraer_segmento(path_original, n):
    """Extrae el segmento optimizado con búsqueda de silencio y reset de reloj"""
    # Calculamos el inicio matemático
    inicio_teorico = (n - 1) * config.CLIP_DURATION
    
    # Buscamos el mejor momento para cortar (Inteligencia Auditiva)
    duracion_optima = obtener_punto_silencio(path_original, inicio_teorico)
    
    path_salida = f"{config.TEMP_FOLDER}/raw_{n}.mp4"
    
    # --- COMANDO OPTIMIZADO ---
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(inicio_teorico),         # Búsqueda rápida
        '-t', str(duracion_optima),         # Duración inteligente
        '-i', path_original,
        '-c', 'copy',                       # Copia directa (sin pérdida)
        '-avoid_negative_ts', 'make_zero',  # Fundamental para que inicie en 00:00
        '-map_metadata', '-1',              # Elimina basura de metadatos viejos
        '-reset_timestamps', '1',           # Evita que Telegram se trabe
        path_salida
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return path_salida
