from PIL import Image, ImageFilter
import os

def preparar_portada_imperial(input_path, output_path):
    """
    Ajusta cualquier imagen al formato vertical 1080x1920.
    Si la imagen es horizontal, crea un efecto de fondo borroso.
    """
    try:
        target_size = (1080, 1920)
        img = Image.open(input_path).convert("RGB")
        
        # 1. Calculamos proporciones
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio == target_ratio:
            # Si ya es perfecta, solo redimensionamos
            final_img = img.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # Si no es vertical, creamos fondo borroso (estilo profesional)
            background = img.resize(target_size, Image.Resampling.LANCZOS)
            background = background.filter(ImageFilter.GaussianBlur(radius=20))
            
            # Ajustamos la imagen original para que quepa al ancho
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Centramos la imagen sobre el fondo borroso
            offset = (0, (target_size[1] - new_height) // 2)
            background.paste(img_resized, offset)
            final_img = background

        final_img.save(output_path, quality=95)
        return True
    except Exception as e:
        print(f"❌ [EDITAR ERROR] {e}")
        return False
