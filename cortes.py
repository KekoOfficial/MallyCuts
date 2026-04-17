import ffmpeg
import os

def procesar_segmento(video_in, foto_in, inicio, duracion, salida):
    """Corta un segmento de 60s e inyecta la portada."""
    try:
        (ffmpeg.input(video_in, ss=inicio, t=duracion)
         .overlay(ffmpeg.input(foto_in), enable='between(t,0,0.05)')
         .output(salida, vcodec='libx264', preset='ultrafast', acodec='aac',
                 video_bitrate='3.8M', maxrate='4M', bufsize='6M',
                 pix_fmt='yuv420p', loglevel="error")
         .overwrite_output().run(quiet=True))
        return True
    except:
        return False
