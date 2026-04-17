import subprocess
import os

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo, portada_p):
    """
    Recibe 7 argumentos. El último es la ruta de la portada 
    seleccionada desde el panel HTML.
    """
    
    # Comando optimizado para Termux
    comando = [
        "ffmpeg", "-y",
        "-ss", str(inicio),             # Tiempo de inicio
        "-t", "60",                     # 60 segundos por clip
        "-i", input_p,                  # El video original
        "-i", portada_p,                # La portada que subiste
        "-filter_complex", "[0:v][1:v]overlay=enable='between(t,0,0.05)'",
        "-c:v", "libx264", 
        "-preset", "ultrafast",         # Clave para que no tarde horas
        "-pix_fmt", "yuv420p", 
        "-c:a", "aac", 
        "-b:a", "128k", 
        output_p
    ]
    
    # Ejecución en segundo plano
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Retorna el texto para Telegram
    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
