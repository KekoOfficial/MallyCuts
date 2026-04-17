import ffmpeg, os, config

def procesar_segmento(v_abs, p_abs, out_p, inicio):
    """Corta, inyecta portada y aplica marca de agua sutil."""
    try:
        v_in = ffmpeg.input(v_abs, ss=inicio, t=config.CLIP_DURATION)
        p_in = ffmpeg.input(p_abs)
        
        # Inyección de portada (0.05s) + Marca de agua estática
        v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
        v_final = v_final.drawtext(
            text=config.WATERMARK_TEXT, 
            x='main_w-text_w-10', y='main_h-text_h-10',
            fontsize=config.WATERMARK_SIZE, 
            fontcolor=config.WATERMARK_COLOR
        )
        
        (ffmpeg.output(v_final, v_in.audio, out_p, 
                       vcodec='libx264', preset='ultrafast', 
                       acodec='aac', video_bitrate='4.5M',
                       pix_fmt='yuv420p', map_metadata=-1, loglevel="error")
         .overwrite_output().run(capture_stdout=True, capture_stderr=True))
        return True
    except:
        return False
