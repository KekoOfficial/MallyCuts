import time

class MallyLogger:
    def __init__(self, nombre_serie, total_capitulos):
        self.nombre = nombre_serie.replace('&', '').replace('<', '').replace('>', '')
        self.total = total_capitulos
        self.inicio_time = time.time()

    def inicio(self):
        """Aviso de inicio de producción"""
        return (
            f"🎬 <b>PRODUCCIÓN INICIADA</b>\n"
            f"📂 Serie: <code>{self.nombre}</code>\n"
            f"🕹️ Capítulos totales: {self.total}\n"
            f"⚡ @MallySeries"
        )

    def cortando(self, n):
        """Estado de procesamiento en consola"""
        return f"⚙️ Procesado cortado: Capítulo {n}/{self.total}"

    def exito(self, n):
        """Mensaje de confirmación para el caption del video"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🕹️ Capítulo: {n}/{self.total}\n"
            f"🌋 Enviado\n"
            f"📨 Enviado {n}\n"
            f"🎉 Logrado\n"
            f"✅ @MallySeries"
        )

    def error(self, n, e):
        """Reporte de fallo"""
        return f"❌ Error en Capítulo {n}: {e}"

    def final(self):
        """Resumen al terminar toda la serie"""
        duracion = int(time.time() - self.inicio_time)
        minutos = duracion // 60
        segundos = duracion % 60
        return (
            f"✅ <b>PROCESADOS TODOS LOS CLIPS</b>\n"
            f"🎬 Serie: {self.nombre}\n"
            f"📦 Total: {self.total} partes\n"
            f"⏱️ Tiempo total: {minutos}m {segundos}s\n"
            f"🎉 ¡Misión cumplida! @MallySeries"
        )

# Funciones de acceso rápido para mantener compatibilidad
def log_inicio(n, t): return MallyLogger(n, t).inicio()
def log_procesando(n, t): return f"⚙️ Procesado cortado: Capítulo {n}/{t}"
def log_exito(n, t): return f"📨 Enviado {n}\n🎉 Logrado"
