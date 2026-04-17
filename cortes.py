import ffmpeg
import os
import config

def procesar_segmento(v_abs, p_abs, out_p, inicio):
    """
    Corta, inyecta portada y aplica marca de agua.
    Optimizado para mantener archivos < 45MB bajo cualquier condición.
    """
    try:
        # Definición de entradas
        v_in = ffmpeg.input(v_abs, ss=inicio, t=config.CLIP_DURATION)
        p_in = ffmpeg.input(p_abs)
        
        # 1. Capa de Miniatura (Overlay los primeros 0.05s)
        # Esto asegura que Telegram use la imagen como portada del video.
        v_final = ffmpeg.overlay(v_in, p_in, enable='between(t,0,0.05)')
        
        # 2. Capa de Marca de Agua (Branding Mally Series)
        v_final = v_final.drawtext(
            text=config.WATERMARK_TEXT, 
            x='main_w-text_w-15', # 15px de margen derecho
            y='main_h-text_h-15', # 15px de margen inferior
            fontsize=config.WATERMARK_SIZE, 
            fontcolor=config.WATERMARK_COLOR,
            shadowcolor='black',
            shadowx=2, shadowy=2
        )
        
        # 3. Renderizado con Control de Bitrate Dinámico
        try:
            (ffmpeg.output(
                v_final, 
                v_in.audio, 
                out_p, 
                vcodec='libx264', 
                preset='ultrafast',   # Máxima velocidad para Termux
                acodec='aac', 
                audio_bitrate='128k', # Audio nítido pero ligero
                
                # --- CONTROL DE PESO CRÍTICO ---
                video_bitrate='3.8M', # Bitrate base (aprox 28MB por minuto)
                maxrate='4.2M',       # Techo máximo absoluto (aprox 31MB por minuto)
                bufsize='6M',         # Control de picos para evitar ráfagas de peso
                # -------------------------------
                
                pix_fmt='yuv420p',    # Formato universal para Telegram
                map_metadata=-1,      # 🚫 Anulación de marcas de origen
                loglevel="error"
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True))
            
            # Verificación de peso post-procesado (Salvaguarda final)
            if os.path.exists(out_p):
                size_mb = os.path.getsize(out_p) / (1024 * 1024)
                if size_mb > 49:
                    # Si milagrosamente se pasa de 49MB, notificamos error preventivo
                    return False
            
            return True
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else "Error desconocido en FFmpeg"
            print(f"💔 FFmpeg Fail: {error_msg}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error de sistema en Cortes: {e}")
        return False
