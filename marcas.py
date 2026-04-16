import config

def obtener_filtro():
    """Retorna la cadena de filtro para FFmpeg"""
    return (
        f"drawtext=text='{config.WATERMARK_TEXT}':x=10:y=H-th-10:"
        f"fontcolor={config.WATERMARK_COLOR}:fontsize={config.WATERMARK_SIZE}:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )
