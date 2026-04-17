import subprocess
import os
import config

def ejecutar_corte(video_in, video_out, inicio, portada, parte, total, titulo):
    """Motor de procesamiento de alto rendimiento."""
    comando = [
        "ffmpeg", "-y",
        "-ss", str(inicio), "-t", "60", # Seek rápido
        "-i", video_in,
        "-i", portada,
        "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=yuv420",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", config.CRF_QUALITY,
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        video_out
    ]
    
    try:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
    except subprocess.CalledProcessError as e:
        print(f"[❌] Error FFmpeg en parte {parte}: {e.stderr.decode()}")
        return None
