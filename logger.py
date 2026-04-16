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
            f"⚡ <i>Calidad Premium Imperio MP</i>"
        )

    def final(self):
        """Genera el reporte de cierre para el canal"""
        fin = datetime.datetime.now()
        duracion = fin - self.inicio
        return (
            f"👑 <b>MISIÓN COMPLETADA</b> 👑\n\n"
            f"🎥 Serie: {self.nombre}\n"
            f"📦 Capítulos subidos: {self.total}\n"
            f"⏱️ Tiempo total: {str(duracion).split('.')[0]}\n\n"
            f"✅ Todos los archivos procesados y sincronizados."
        )
