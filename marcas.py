# marcas.py - El Sello de Umbrae Studio
import config

def obtener_filtro_agua():
    """Filtro avanzado con doble red social y sombra"""
    # Texto combinado para la esquina inferior
    texto_marca = f"TG: MallySeries | TT: EscenaDe15"
    
    filtro = (
        f"drawtext=text='{texto_marca}':"
        f"x=w-tw-20:y=h-th-20:" # Posición pro en esquina
        f"fontsize={config.WATERMARK_SIZE}:"
        f"fontcolor={config.WATERMARK_COLOR}:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )
    return filtro

def aplicar_metadatos_cmd(n_cap):
    """Firma digital invisible de Umbrae Studio"""
    return [
        '-metadata', f'title=Cap {n_cap} - Mally Series',
        '-metadata', 'artist=Umbrae Studio',
        '-metadata', 'copyright=Copyright © 2026 Umbrae Studio',
        '-metadata', 'comment=Distribuido por EscenaDe15'
    ]
