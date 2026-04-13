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
                f"⚙️ <i>Modo Cascada: 60s + Marca de Agua</i>\n"
                f"⚡ @MallySeries")

    def cortando(self, n):
        return f"Procesando bloque: {n}/{self.total}"

    def exito(self, n):
        return (f"🎬 <b>{self.nombre}</b>\n"
                f"🕹️ Capítulo: {n}/{self.total}\n"
                f"✅ @MallySeries")

    def final(self):
        dur = int(time.time() - self.inicio_time)
        return (f"✅ <b>{self.nombre} FINALIZADA</b>\n"
                f"⏱️ Tiempo total: {dur//60}m {dur%60}s\n"
                f"🎉 @MallySeries")
