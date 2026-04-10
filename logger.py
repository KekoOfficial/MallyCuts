import time

class MallyLogger:
    def __init__(self, nombre_serie, total_capitulos):
        # Mantenemos el nombre real pero escapamos caracteres que rompen el HTML de Telegram
        self.nombre = (nombre_serie.replace('&', '&amp;')
                                   .replace('<', '&lt;')
                                   .replace('>', '&gt;'))
        self.total = total_capitulos
        self.inicio_time = time.perf_counter()

    def inicio(self):
        """Aviso de inicio de producción"""
        return (
            "🎬 <b>PRODUCCIÓN INICIADA</b>\n\n"
            f"📂 Serie: <b>{self.nombre}</b>\n"
            f"🕹️ Capítulos totales: <code>{self.total}</code>\n\n"
            "⚡ @MallySeries"
        )

    def cortando(self, n):
        """Estado de procesamiento en consola (sin tags HTML)"""
        return f"⚙️ Procesado cortado: Capítulo {n}/{self.total}"

    def exito(self, n):
        """Mensaje estético para el caption del video"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🕹️ Capítulo: <b>{n}/{self.total}</b>\n"
            "🌋 Corta vídeo Automáticamente\n"
            f"📨 Enviado: <code>{n}</code>\n"
            "🎉 Creador: <b>Khassam.//Dev</b>\n"
            "✅ @MallySeries"
        )

    def error(self, n, e):
        """Reporte de fallo con formato técnico"""
        return f"❌ <b>Error en Capítulo {n}</b>\n<code>{e}</code>"

    def final(self):
        """Resumen final con cronómetro de precisión"""
        duracion = int(time.perf_counter() - self.inicio_time)
        mm, ss = divmod(duracion, 60)
        return (
            "✅ <b>PROCESADOS TODOS LOS CLIPS</b>\n\n"
            f"🎬 Serie: <b>{self.nombre}</b>\n"
            f"📦 Total: <code>{self.total} partes</code>\n"
            f"⏱️ Tiempo total: <b>{mm}m {ss}s</b>\n\n"
            "🎉 ¡Misión cumplida! @MallySeries"
        )

# Funciones de acceso rápido optimizadas
def log_inicio(n, t): return MallyLogger(n, t).inicio()
def log_procesando(n, t): return f"⚙️ Procesando: Capítulo {n}/{t}"
def log_exito(n, t): return f"📨 Enviado {n}\n🎉 Logrado"
