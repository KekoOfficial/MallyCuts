import subprocess

def ejecutar_corte(input_p, output_p, inicio, parte, total, titulo, portada_p):
    """
    Corte ULTRA RÁPIDO (Sin portada, solo clonado)
    """
    comando = [
        "ffmpeg",
        "-y",
        "-ss", str(inicio),
        "-i", input_p,
        "-t", "60",
        "-c", "copy", # 🔥 Velocidad instantánea
        "-avoid_negative_ts", "make_zero",
        output_p
    ]

    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return f"🎬 {titulo}\n💎 PARTE: {parte}/{total}\n🔗 @MallySeries"
