import requests
import time
import os
from config import *
from core.logger import log

# 🌐 CONFIGURACIÓN DE SESIÓN PARA MAYOR ESTABILIDAD
session = requests.Session()
session.trust_env = False  # Evita problemas con proxies o DNS

def enviar_a_telegram(ruta_archivo, caption):
    """
    Envía video a Telegram con sistema de reintentos y manejo de errores.
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"

    if not os.path.exists(ruta_archivo):
        log.error(f"❌ Archivo no encontrado: {ruta_archivo}")
        return False

    tamaño_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)
    log.info(f"📤 Enviando [{tamaño_mb:.1f} MB]...")

    for intento in range(REINTENTOS_ENVIO):
        try:
            with open(ruta_archivo, "rb") as f:
                respuesta = session.post(
                    url,
                    data={
                        "chat_id": CHAT_ID,
                        "caption": caption,
                        "supports_streaming": True,
                        "parse_mode": "HTML"  # Opcional: Permite usar negritas y estilos
                    },
                    files={"video": f},
                    timeout=TIMEOUT_TELEGRAM
                )

            if respuesta.status_code == 200:
                log.info(f"✅ Enviado correctamente ✔️")
                os.remove(ruta_archivo)  # 🗑️ Borramos después de enviar
                time.sleep(PAUSA_ENTRE_ENVIOS)
                return True

            elif respuesta.status_code == 429:
                # Manejo de límite de velocidad de Telegram
                datos = respuesta.json()
                espera = datos.get('parameters', {}).get('retry_after', 15)
                log.warning(f"⏳ Esperando {espera}s (límite de velocidad)...")
                time.sleep(espera)

            else:
                log.warning(f"⚠️ Error {respuesta.status_code} | Intento {intento+1}/{REINTENTOS_ENVIO}")
                # Intentar mostrar mensaje de error de Telegram
                try:
                    error_msg = respuesta.json().get('description', 'Desconocido')
                    log.error(f"ℹ️ Detalle: {error_msg}")
                except:
                    pass
                time.sleep(5)

        except requests.exceptions.Timeout:
            log.error(f"⏱️ Tiempo de espera agotado. Reintentando...")
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            log.error(f"📡 Error de conexión. Reintentando...")
            time.sleep(10)
        except Exception as e:
            log.error(f"💥 Error inesperado: {str(e)}")
            time.sleep(5)

    log.error(f"⛔ Falló el envío después de {REINTENTOS_ENVIO} intentos")
    return False
