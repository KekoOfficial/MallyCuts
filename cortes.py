import subprocess
import config

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo):
    # Comando optimizado para velocidad en móviles
    comando = [
        "ffmpeg", "-y", "-ss", str(inicio), "-t", "60",
        "-i", input_p, "-i", config.FOTO_PORTADA,
        "-filter_complex", "[0:v][1:v]overlay=enable='between(t,0,0.05)'",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", output_p
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
