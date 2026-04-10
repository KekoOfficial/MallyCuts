import time

class MallyLogger:
    def __init__(self, nombre_serie, total_capitulos):
        # Limpieza de caracteres prohibidos en HTML y nombres de archivos
        self.nombre = "".join(c for c in nombre_serie if c not in ('&', '<', '>', '/', '\\', '*', '?', '"', '|'))
        self.total = total_capitulos
        self.inicio_time = time.perf_counter() # Más preciso para medir duraciones

    def inicio(self):
        """Aviso de inicio de producción con formato limpio"""
        return (
            "🎬 <b>PRODUCCIÓN INICIADA</b>\n"
            f"📂 Serie: <code>{self.nombre}</code>\n"
            f"🕹️ Capítulos totales: <b>{self.total}</b>\n"
            "⚡ @MallySeries"
        )

    def cortando(self, n):
        """Estado de procesamiento en consola"""
        return f"⚙️ Procesado cortado: Capítulo {n}/{self.total}"

    def exito(self, n):
        """Mensaje de confirmación para el caption del video (Telegram ready)"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🕹️ Capítulo: <b>{n}/{self.total}</b>\n"
            f"🌋 Corta vídeo Automáticamente\n"
            f"📨 Enviado {n}\n"
            f"🎉 Creador: <b>Khassam.//Dev</b>\n"
            f"✅ @MallySeries"
        )

    def error(self, n, e):
        """Reporte de fallo detallado"""
        return f"❌ Error en Capítulo {n}: <code>{e}</code>"

    def final(self):
        """Resumen final con cálculo de tiempo optimizado"""
        duracion = int(time.perf_counter() - self.inicio_time)
        mm, ss = divmod(duracion, 60)
        return (
            "✅ <b>PROCESADOS TODOS LOS CLIPS</b>\n"
            f"🎬 Serie: <code>{self.nombre}</code>\n"
            f"📦 Total: <b>{self.total}</b> partes\n"
            f"⏱️ Tiempo total: <b>{mm}m {ss}s</b>\n"
            "🎉 ¡Misión cumplida! @MallySeries"
        )

# Funciones de acceso rápido (Mantenidas para compatibilidad con main.py)
def log_inicio(n, t): return MallyLogger(n, t).inicio()
def log_procesando(n, t): return f"⚙️ Procesando: Capítulo {n}/{t}"
def log_exito(n, t): return f"📨 Enviado {n}\n🎉 Logrado"
