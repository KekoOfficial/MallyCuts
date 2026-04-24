// ==============================================
// 📥 CONTROLADOR DESCARGAS - MALLYCUTS
// ==============================================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formularioDescarga');
    const estado = document.getElementById('estado');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = document.getElementById('urlInput').value;
        const nombre = document.getElementById('nombreInput').value;
        const cortar = document.getElementById('cortarCheck').checked;
        const velocidad = document.getElementById('velocidadCheck').checked;

        estado.innerHTML = "⏳ <b>ENVIANDO SOLICITUD...</b>";
        estado.style.color = "#ffcc00";

        try {
            const respuesta = await fetch('/enlaces/procesar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    titulo: nombre,
                    opciones: { cortar, velocidad }
                })
            });

            const data = await respuesta.json();

            if(data.status === 'ok') {
                estado.innerHTML = `✅ ${data.mensaje}`;
                estado.style.color = "#00ff88";
            } else {
                throw new Error(data.mensaje);
            }

        } catch (error) {
            estado.innerHTML = `❌ ERROR: ${error.message}`;
            estado.style.color = "#ff4444";
        }
    });
});
