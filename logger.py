import config

class MallyLogger:
    def __init__(self, nombre, total_caps):
        """
        Iniciador de identidad Umbrae Studio.
        """
        self.nombre = nombre.upper()
        self.total_caps = total_caps
        self.canal = config.WATERMARK_TEXT.replace("t.me/", "@")

    def portada_msg(self, desc):
        """
        Banner de inicio de serie con estética de plataforma.
        """
        descripcion = desc if desc else "Sin descripción oficial disponible."
        return (
            f"🎬 <b>ESTRENO EXCLUSIVO</b>\n"
            f"───────────────────────\n"
            f"🏆 <b>{self.nombre}</b>\n\n"
            f"📝 <b>SINOPSIS:</b>\n<i>{descripcion}</i>\n\n"
            f"📦 <b>ENTREGA:</b> {self.total_caps} Capítulos\n"
            f"📡 <b>CANAL:</b> {self.canal}\n"
            f"───────────────────────\n"
            f"⚡ <i>By Umbrae Studio Core V3.1</i>"
        )

    def exito(self, n):
        """
        Caption individual para capítulos con barra de progreso visual.
        """
        # Barra de progreso visual sutil
        progreso = "▰" * int((n/self.total_caps)*10) + "▱" * (10 - int((n/self.total_caps)*10))
        
        return (
            f"🎥 <b>{self.nombre}</b>\n"
            f"📺 <b>CAPÍTULO:</b> {n} / {self.total_caps}\n"
            f"⏳ <code>[{progreso}]</code>\n"
            f"───────────────────────\n"
            f"🚀 {self.canal} | @EscenaDe15"
        )

    def final(self):
        """
        Reporte final de misión completada.
        """
        return (
            f"🏆 <b>MISIÓN FINALIZADA</b>\n"
            f"───────────────────────\n"
            f"✅ <b>Serie:</b> {self.nombre}\n"
            f"📦 <b>Estado:</b> {self.total_caps} Caps Subidos\n"
            f"💎 <b>Calidad:</b> Premium Express\n\n"
            f"🔥 <i>¡Disfruta en @MallySeries!</i>"
        )
