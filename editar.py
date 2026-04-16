from PIL import Image, ImageFilter
import os

def preparar_portada_imperial(input_path, output_path):
    """Ajusta imagen a 1080x1920 con fondo borroso si es necesario."""
    try:
        target_size = (1080, 1920)
        img = Image.open(input_path).convert("RGB")
        img_ratio = img.width / img.height
        
        # Crear base borrosa
        bg = img.resize(target_size, Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=25))
        
        # Ajustar imagen original al ancho sin deformar
        new_w = target_size[0]
        new_h = int(new_w / img_ratio)
        img_res = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Pegar en el centro
        offset = (0, (target_size[1] - new_h) // 2)
        bg.paste(img_res, offset)
        bg.save(output_path, quality=95)
        return True
    except: return False
