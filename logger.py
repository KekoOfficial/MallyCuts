import time

class MallyLogger:
    def __init__(self, nombre_serie, total_capitulos):
        self.nombre = nombre_serie.replace('&', '').replace('<', '').replace('>', '')
        self.total = total_capitulos
        self.inicio_time = time.time()

    def portada_msg(self, descripcion):
        return (
            f"🎬 <b>MALLY SERIES PRESENTA:</b>\n"
            f"🍿 <b>{self.nombre}</b>\n\n"
            f"📝 {descripcion}\n"
            f"⚙️ <i>Procesando capítulos de 3 minutos...</i>\n"
            f"⚡ @MallySeries"
        )

    def exito(self, n):
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🕹️ Capítulo: {n}/{self.total}\n"
            f"🌋 Enviado\n"
            f"📨 Enviado {n}\n"
            f"🎉 Logrado\n"
            f"✅ @MallySeries"
        )

    def final(self):
        duracion = int(time.time() - self.inicio_time)
        return (
            f"✅ <b>{self.nombre} FINALIZADA</b>\n"
            f"📦 Total: {self.total} partes\n"
            f"⏱️ Tiempo: {duracion//60}m {duracion%60}s\n"
            f"🎉 @MallySeries"
        )
