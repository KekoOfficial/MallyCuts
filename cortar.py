import subprocess
import config
import os

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo):
    """
    Realiza el corte de 60 segundos, inyecta la portada y 
    devuelve el caption listo para Telegram.
    """
    # Verificamos si la portada existe para evitar errores de FFmpeg
    if not os.path.exists(config.FOTO_PORTADA):
        print(f"⚠️ Advertencia: No se encontró {config.FOTO_PORTADA}")
    
    # Comando optimizado para velocidad en procesadores móviles (Termux)
    comando = [
        "ffmpeg", "-y", 
        "-ss", str(inicio), 
        "-t", "60",
        "-i", input_p, 
        "-i", config.FOTO_PORTADA,
        "-filter_complex", "[0:v][1:v]overlay=enable='between(t,0,0.05)'",
        "-c:v", "libx264", 
        "-preset", "ultrafast", 
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", 
        "-b:a", "128k", 
        output_p
    ]
    
    # Ejecución silenciosa
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Retorna el texto que acompañará al video en el canal
    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
