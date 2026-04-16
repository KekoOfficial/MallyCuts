import subprocess
import os
import config

def procesar_segmento(video_input, n_capitulo):
    if not os.path.exists(config.TEMP_FOLDER):
        os.makedirs(config.TEMP_FOLDER)
        
    output_path = f"{config.TEMP_FOLDER}/cap_{n_capitulo}.mp4"
    start_time = (n_capitulo - 1) * config.CLIP_DURATION
    
    # Filtro de marca de agua avanzado (Esquina inferior derecha)
    filtro_watermark = f"drawtext=text='{config.WATERMARK_TEXT}':x=w-tw-20:y=h-th-20:fontsize={config.WATERMARK_SIZE}:fontcolor={config.WATERMARK_COLOR}"
    
    cmd = [
        'ffmpeg', '-y', '-ss', str(start_time), '-t', str(config.CLIP_DURATION),
        '-i', video_input,
        '-vf', filtro_watermark,
        '-c:v', config.VIDEO_CODEC, '-preset', config.PRESET, '-crf', config.CRF_VALUE,
        '-c:a', 'copy', output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except Exception as e:
        print(f"❌ Error en corte del Cap {n_capitulo}: {e}")
        return None
