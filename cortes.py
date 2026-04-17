import ffmpeg, os

def procesar_segmento(v_abs, p_abs, out_p, inicio, duracion):
    """Corta el video e inyecta la portada con bitrate optimizado."""
    v_in = ffmpeg.input(v_abs, ss=inicio, t=duracion)
    p_in = ffmpeg.input(p_abs)
    
    # Overlay de 0.05s para la miniatura
    v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
    
    try:
        (ffmpeg.output(v_final, v_in.audio, out_p, 
                       vcodec='libx264', preset='ultrafast', 
                       acodec='aac', video_bitrate='4.5M',
                       pix_fmt='yuv420p', map_metadata=-1, loglevel="error")
         .overwrite_output().run(capture_stdout=True, capture_stderr=True))
        return True
    except:
        return False
