import os
import sys
import time
import telebot
# Importa la infraestructura unificada y el logger
try:
    import config as cfg
    import logger
except ImportError:
    print("❌ Errorenviar: No se encontró config.py o logger.py.")
    sys.exit(1)

# Inicialización silenciosa del Bot para subida unificada
bot = telebot.TeleBot(cfg.BOT_TOKEN)

def subir_media_telegram(video_processed_path, portada_path, nombre_serie, descripcion, chapter):
    """
    DELEGADO: Envía el video procesado y la portada al canal oficial Mally Series.
    Aplica reintentos automáticos sincronizados.
    """
    logger.registrar_log(f"📡 [TELEGRAM CAP{chapter}] Iniciando subida de segmento a {cfg.TG_OFFICIAL}...")
    
    # Caption unificado para capítulos cortos (Mally Series Style)
    caption_imperial = (
        f"👑 <b>{cfg.STUDIO_NAME.upper()} PRESENTA:</b>\n"
        f"───────────────────\n"
        f"🎬 <b>{nombre_serie} • Capítulo {chapter}</b>\n"
        f"📝 <b>Info:</b> {descripcion}\n"
        f"───────────────────\n"
        f"📡 <b>Oficial:</b> {cfg.TG_OFFICIAL}\n"
        f"🎥 <b>TikTok:</b> {cfg.TT_OFFICIAL}\n"
        f"⚡ <i>Umbrae Sincronizado V3.1 (AutoCortes)</i>"
    )
    
    retries = 0
    while retries < cfg.MAX_RETRIES:
        try:
            # Abrir archivos en modo binario para envío
            with open(video_processed_path, 'rb') as video_file, open(portada_path, 'rb') as photo_file:
                
                # Enviar video con portada (thumb) y caption HTML
                bot.send_video(
                    cfg.CHAT_ID_CANAL, 
                    video_file, 
                    caption=caption_imperial, 
                    parse_mode="HTML",
                    thumb=photo_file, # Usar la portada subida como miniatura
                    supports_streaming=True, # Permitir reproducir sin descargar completo
                    timeout=cfg.TIMEOUT_SEND # Tiempo de espera para archivos grandes
                )
                
            logger.registrar_log(f"🏆 [EXITO TELEGRAM CAP{chapter}] Publicado oficialmente en {cfg.TG_OFFICIAL}.")
            return True # Retorna True si tiene éxito la subida
            
        except Exception as e:
            retries += 1
            logger.registrar_log(f"⚠️ [REINTENTO CAP{chapter} {retries}/{cfg.MAX_RETRIES}] Error enviando a Telegram: {str(e)}")
            time.sleep(10) # Esperar antes de reintentar
            
    logger.registrar_log(f"❌ [FALLO TOTAL CAP{chapter}] No se pudo enviar el segmento tras {cfg.MAX_RETRIES} intentos.")
    return False # Retorna False si falla la subida total
