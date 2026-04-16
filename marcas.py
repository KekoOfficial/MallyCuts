# marcas.py - El Sello de Umbrae Studio
import config

def obtener_filtro_agua():
    """Retorna la cadena de filtros para la marca de agua"""
    texto = config.WATERMARK_TEXT # t.me/MallySeries
    size = config.WATERMARK_SIZE
    color = config.WATERMARK_COLOR
    
    filtro = (
        f"drawtext=text='{texto}':"
        f"x=w-tw-20:y=h-th-20:"
        f"fontsize={size}:"
        f"fontcolor={color}:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )
    return filtro

def aplicar_metadatos_cmd(n_cap):
    """Metadatos que firman el archivo como Umbrae Studio"""
    return [
        '-metadata', f'title=Cap {n_cap} - {config.WATERMARK_TEXT}',
        '-metadata', 'artist=Umbrae Studio',
        '-metadata', 'album=Mally Series',
        '-metadata', 'comment=Copyright © 2026 Umbrae Studio'
    ]
