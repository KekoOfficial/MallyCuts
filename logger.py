# logger.py - El Cerebro de Umbrae Studio
import datetime

class MallyLogger:
    def __init__(self, nombre_serie, total_caps):
        self.nombre = nombre_serie
        self.total = total_caps
        self.inicio = datetime.datetime.now()

    def exito(self, n):
        """Genera el caption con la identidad multi-plataforma"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🔹 Capítulo: {n} / {self.total}\n\n"
            f"📱 <b>Síguenos en:</b>\n"
            f"• Telegram: t.me/MallySeries\n"
            f"• TikTok: @EscenaDe15\n\n"
            f"⚡ <i>By #UmbraeStudio</i>"
        )

    def final(self):
        """Reporte de Misión Completada"""
        fin = datetime.datetime.now()
        duracion = str(fin - self.inicio).split('.')[0]
        return (
            f"👑 <b>MISIÓN COMPLETADA</b> 👑\n\n"
            f"🎥 Serie: <b>{self.nombre}</b>\n"
            f"📦 Capítulos: {self.total}\n"
            f"⏱️ Tiempo: {duracion}\n\n"
            f"✅ <i>Sincronización total por Umbrae Studio.</i>"
        )
