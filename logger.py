import time

class MallyLogger:
    def __init__(self, nombre, total):
        self.nombre = nombre.strip().upper()
        self.total = total
        self.inicio = time.time()

    def portada_msg(self, desc):
        return (f"💎 <b>MALLY SERIES • PREMIUM</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎬 <b>PRODUCCIÓN:</b> {self.nombre}\n"
                f"📝 <b>RESEÑA:</b> {desc}\n"
                f"📦 <b>CAPÍTULOS:</b> {self.total}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🛰️ <i>Procesando en alta prioridad...</i>")

    def cortando(self, n):
        return f"⚡ [MODO IMPERIO] Renderizando bloque {n}/{self.total}"

    def exito(self, n):
        return (f"🎬 <b>{self.nombre}</b>\n"
                f"💎 <b>CAPÍTULO:</b> {n} / {self.total}\n"
                f"✅ <i>Contenido Verificado</i>\n"
                f"🔗 @MallySeries")

    def final(self):
        m, s = divmod(int(time.time() - self.inicio), 60)
        return (f"🏁 <b>DISTRIBUCIÓN COMPLETADA</b>\n"
                f"📊 <b>Partes:</b> {self.total}\n"
                f"⏱️ <b>Tiempo:</b> {m}m {s}s\n"
                f"👑 <b>Umbrae Studio</b>")
