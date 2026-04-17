import subprocess
import os

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo, portada_p):
    # Verificamos si la portada existe antes de intentar usarla
    if not os.path.exists(portada_p):
        print(f"[⚠️] Portada no encontrada en {portada_p}. Cortando sin portada.")
        comando = [
            "ffmpeg", "-y", "-ss", str(inicio), "-t", "60",
            "-i", input_p, "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "28", "-c:a", "aac", "-b:a", "96k", output_p
        ]
    else:
        comando = [
            "ffmpeg", "-y", "-ss", str(inicio), "-t", "60",
            "-i", input_p, "-i", portada_p,
            # Filtro mejorado para evitar pantalla negra
            "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=yuv420",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "28", "-c:a", "aac", "-b:a", "96k", 
            "-movflags", "+faststart", output_p
        ]
    
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
