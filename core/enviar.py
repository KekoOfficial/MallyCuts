import requests
from config import TOKEN, CHAT_ID

def enviar_video(ruta_archivo, titulo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    
    # 🎨 Formato exacto que pediste
    caption = f"""🎬 {titulo}
💎 CAPÍTULO: 114 / 114
✅ Contenido Verificado
🔗 @MallySeries"""
    
    try:
        with open(ruta_archivo, "rb") as archivo:
            datos = {
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            }
            archivos = {
                "video": archivo
            }
            respuesta = requests.post(url, data=datos, files=archivos)
            
        if respuesta.status_code == 200:
            print("✅ Enviado correctamente")
            return True
        else:
            print(f"❌ Error API: {respuesta.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error envío: {str(e)}")
        return False
