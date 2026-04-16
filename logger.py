# logger.py - El Cerebro de Mally Series
import datetime

class MallyLogger:
    def __init__(self, nombre_serie, total_caps):
        self.nombre = nombre_serie
        self.total = total_caps
        self.inicio = datetime.datetime.now()

    def exito(self, n):
        """Genera el caption para cada video enviado"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🔹 Capítulo: {n} / {self.total}\n\n"
            f"✨ Disfruta en @MallySeries\n"
            f"⚡ <i>Creado por #UmbraeStudio</i>"
        )

    def final(self):
        """Genera el reporte de cierre para el canal"""
        fin = datetime.datetime.now()
        duracion = fin - self.inicio
        tiempo_formateado = str(duracion).split('.')[0]
        
        return (
            f"👑 <b>MISIÓN COMPLETADA</b> 👑\n\n"
            f"🎥 Serie: <b>{self.nombre}</b>\n"
            f"📦 Capítulos subidos: {self.total}\n"
            f"⏱️ Tiempo total: {tiempo_formateado}\n\n"
            f"✅ <i>Procesado y Sincronizado por Umbrae Studio.</i>"
        )
