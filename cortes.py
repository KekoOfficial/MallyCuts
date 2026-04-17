import subprocess
import os

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo, portada_p):
    """
    Corta 60 segundos del video de entrada, aplica la portada seleccionada
    como un flash inicial de 0.05s y exporta el clip.
    """
    
    # Comando optimizado para Termux (procesadores ARM de móvil)
    comando = [
        "ffmpeg", "-y",
        "-ss", str(inicio),             # Tiempo de inicio
        "-t", "60",                     # Duración del corte
        "-i", input_p,                  # Entrada de Video
        "-i", portada_p,                # Entrada de Portada
        "-filter_complex", "[0:v][1:v]overlay=enable='between(t,0,0.05)'",
        "-c:v", "libx264", 
        "-preset", "ultrafast",         # Máxima velocidad de proceso
        "-pix_fmt", "yuv420p", 
        "-c:a", "aac", 
        "-b:a", "128k", 
        output_p                        # Archivo de salida
    ]
    
    # Ejecutamos sin llenar la consola de basura de FFmpeg
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # El texto que verás en Telegram
    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
