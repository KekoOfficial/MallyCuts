# marcas.py - El Sello Imperial
import config

def obtener_filtro_agua():
    """Retorna la cadena de filtros para FFmpeg"""
    # Posición: Inferior derecha (w-tw-20 : h-th-20)
    # Estilo: Fuente de tamaño configurado y color translúcido
    texto = config.WATERMARK_TEXT
    size = config.WATERMARK_SIZE
    color = config.WATERMARK_COLOR
    
    filtro = (
        f"drawtext=text='{texto}':"
        f"x=w-tw-20:y=h-th-20:"
        f"fontsize={size}:"
        f"fontcolor={color}:"
        f"shadowcolor=black@0.4:shadowx=2:shadowy=2"
    )
    return filtro

def obtener_metadatos(n):
    """Genera metadatos internos para el archivo de video"""
    return {
        "title": f"{config.WATERMARK_TEXT} - Cap {n}",
        "artist": "Imperio MP",
        "comment": "Procesado por MallyCuts v2.1"
    }
