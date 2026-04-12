import time
import os

class MallyLogger:
    def __init__(self, nombre_serie, total_capitulos):
        # 1. Quitamos la extensión si existe (.mp4, .mkv, etc)
        nombre_limpio = os.path.splitext(nombre_serie)[0]
        
        # 2. Escapamos caracteres HTML
        self.nombre = (nombre_limpio.replace('&', '&amp;')
                                    .replace('<', '&lt;')
                                    .replace('>', '&gt;'))
        
        self.total = total_capitulos
        self.inicio_time = time.perf_counter()

    def _fmt_id(self, n):
        """Convierte el número en un ID elegante (001, 002...)"""
        return str(n).zfill(3)

    def inicio(self):
        """Aviso de inicio de producción"""
        return (
            "🎬 <b>PRODUCCIÓN INICIADA</b>\n\n"
            f"📂 Serie/Película: <b>{self.nombre}</b>\n"
            f"🕹️ Capítulos totales: <code>{self.total}</code>\n\n"
            "⚡ @MallySeries"
        )

    def cortando(self, n):
        """Estado de consola"""
        return f"⚙️ Procesado: 🆔 {self._fmt_id(n)} | {self.nombre}"

    def exito(self, n):
        """Caption del video (Sin nombres de archivo feos)"""
        return (
            f"🎬 <b>{self.nombre}</b>\n"
            f"🕹️ Capítulo: <b>{self._fmt_id(n)}/{self.total}</b>\n"
            "🌋 Corta vídeo Automáticamente\n"
            f"📨 Enviado: <code>🆔 {self._fmt_id(n)}</code>\n"
            "🎉 Creador: <b>Khassam.//Dev</b>\n"
            "✅ @MallySeries"
        )

    def error(self, n, e):
        return f"❌ <b>Error en 🆔 {self._fmt_id(n)}</b>\n<code>{e}</code>"

    def final(self):
        duracion = int(time.perf_counter() - self.inicio_time)
        mm, ss = divmod(duracion, 60)
        return (
            "✅ <b>PROCESO FINALIZADO</b>\n\n"
            f"🎬 Título: <b>{self.nombre}</b>\n"
            f"📦 Partes: <code>{self.total}</code>\n"
            f"⏱️ Tiempo: <b>{mm}m {ss}s</b>\n\n"
            "🎉 ¡Misión cumplida! @MallySeries"
        )

# Funciones de acceso rápido mejoradas
def log_inicio(n, t): 
    return MallyLogger(n, t).inicio()

def log_procesando(n, t): 
    return f"⚙️ Procesando: 🆔 {str(n).zfill(3)} | {n}"

def log_exito(n, t): 
    return f"📨 Enviado 🆔 {str(n).zfill(3)}\n🎉 Logrado"
