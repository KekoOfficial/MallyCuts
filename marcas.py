import subprocess
import config

def aplicar_marca_agua(path_input, n):
    path_output = f"{config.TEMP_FOLDER}/cap_{n:03d}.mp4"
    
    # --- LÓGICA ESTILO TIKTOK ---
    # Cambia de posición cada 5 segundos.
    # Posición 1: Arriba Izquierda | Posición 2: Abajo Derecha
    # Aparece y desaparece (fade) suavemente.
    
    # x e y cambian según el tiempo 't' usando la función mod (módulo)
    x_formula = "if(lt(mod(t,10),5), 20, w-tw-20)"
    y_formula = "if(lt(mod(t,10),5), 20, h-th-20)"
    
    # Opacidad intermitente (opcional, para que parpadee como TikTok)
    alpha_formula = "if(lt(mod(t,10),5), 0.5, 0.5)" # 50% de opacidad constante

    filtro = (
        f"drawtext=text='{config.WATERMARK_TEXT}':"
        f"x={x_formula}:y={y_formula}:"
        f"fontcolor={config.WATERMARK_COLOR}:"
        f"fontsize={config.WATERMARK_SIZE}:"
        f"shadowcolor=black@0.5:shadowx=2:shadowy=2"
    )
    
    cmd = [
        'ffmpeg', '-y', '-i', path_input,
        '-vf', filtro,
        '-c:v', 'libx264', 
        '-preset', 'superfast', 
        '-crf', '26', 
        '-threads', '0', 
        '-c:a', 'copy', 
        path_output
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return path_output
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en Marcas.py: {e.stderr.decode()}")
        raise e
