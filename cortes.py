import ffmpeg
import config

def procesar_segmento(v_in, inicio, duracion, salida):
    """Corta 60s e inyecta la portada flash."""
    try:
        (ffmpeg.input(v_in, ss=inicio, t=duracion)
         .overlay(ffmpeg.input(config.FOTO_PORTADA), enable='between(t,0,0.05)')
         .output(salida, vcodec='libx264', preset='ultrafast', acodec='aac',
                 video_bitrate='3.8M', maxrate='4M', bufsize='6M',
                 pix_fmt='yuv420p', loglevel="error")
         .overwrite_output().run(quiet=True))
        return True
    except Exception as e:
        print(f"Error en FFmpeg: {e}")
        return False
