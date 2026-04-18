import subprocess

def cortar_video(ruta_entrada, ruta_salida):
    try:
        print("✂️ Cortando a 60s - Modo 1080p")
        
        comando = [
            "ffmpeg", "-y",
            "-ss", "0",
            "-i", ruta_entrada,
            "-t", "60",                   # ⏱️ Exactos 60 segundos
            "-vf", "scale=1920:1080",    # 📺 Full HD
            "-c:v", "libx264",
            "-preset", "ultrafast",      # ⚡ Velocidad máxima
            "-crf", "23",                # 🎬 Calidad perfecta
            "-c:a", "aac",
            "-b:a", "128k",
            ruta_salida
        ]
        
        resultado = subprocess.run(comando, capture_output=True)
        
        if resultado.returncode == 0:
            return True
        else:
            print(f"❌ Error: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False
