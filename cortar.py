import subprocess

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo, portada_p):
    """
    Balance perfecto: Mantiene portada + Velocidad extrema.
    """
    comando = [
        "ffmpeg",
        "-y",
        "-ss", str(inicio),      # Seek rápido antes del input
        "-i", input_p,           # Video original
        "-i", portada_p,         # Portada
        "-t", "60",              # Duración exacta
        
        # Filtro optimizado: shortest=1 hace que el overlay no pese de más
        "-filter_complex", "[0:v][1:v]overlay=shortest=1",
        
        # Configuración de guerra para Termux
        "-c:v", "libx264",
        "-preset", "ultrafast",  # Máxima velocidad de codificación
        "-crf", "28",            # Calidad balanceada para ahorrar espacio
        "-c:a", "aac",
        "-b:a", "96k",           # Audio ligero
        "-movflags", "+faststart", # Para que el video cargue rápido en Telegram
        
        output_p
    ]

    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
