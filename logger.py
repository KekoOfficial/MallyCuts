import time

class MallyLogger:
    def __init__(self, nombre, total):
        self.nombre = nombre.strip().upper()
        self.total = total
        self.inicio_time = time.time()

    def portada_msg(self, descripcion):
        return (f"🎬 <b>MALLY SERIES PRESENTA:</b>\n"
                f"🍿 <b>{self.nombre}</b>\n\n"
                f"📝 {descripcion}\n"
                f"⚙️ <i>Iniciando cortes de 3 minutos...</i>\n"
                f"⚡ @MallySeries")

    def exito(self, n):
        return (f"🎬 <b>{self.nombre}</b>\n"
                f"🕹️ Capítulo: {n}/{self.total}\n"
                f"🌋 Enviado\n"
                f"📨 Enviado {n}\n"
                f"🎉 Logrado\n"
                f"✅ @MallySeries")

    def final(self):
        dur = int(time.time() - self.inicio_time)
        return (f"✅ <b>{self.nombre} FINALIZADA</b>\n"
                f"📦 Total: {self.total} partes\n"
                f"⏱️ Tiempo: {dur//60}m {dur%60}s\n"
                f"🎉 @MallySeries")
