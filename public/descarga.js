// ==============================================
// 📥 CONTROLADOR DESCARGAS - MALLYCUTS
// ==============================================

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formularioDescarga');
    const estado = document.getElementById('estado');

    // ==============================================
    // 🚀 ENVIAR FORMULARIO
    // ==============================================
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Obtener datos
        const url = document.getElementById('urlInput').value;
        const titulo = document.getElementById('nombreInput').value;
        const cortar = document.getElementById('cortarCheck').checked;
        const velocidad = document.getElementById('velocidadCheck').checked;

        // Cambiar estado a cargando
        estado.innerHTML = "⏳ <b>INICIANDO DESCARGA...</b>";
        estado.style.color = "#ffcc00";
        estado.style.display = "block";

        try {
            // Llamar al servidor
            const respuesta = await fetch('/enlaces/procesar', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    titulo: titulo,
                    opciones: {
                        cortar: cortar,
                        velocidad: velocidad
                    }
                })
            });

            const data = await respuesta.json();

            if(data.status === 'ok') {
                estado.innerHTML = `✅ ${data.mensaje}`;
                estado.style.color = "#00ff88";
            } else {
                throw new Error(data.mensaje || 'Error desconocido');
            }

        } catch (error) {
            estado.innerHTML = `❌ ERROR: ${error.message}`;
            estado.style.color = "#ff4444";
            console.error(error);
        }
    });

    // ==============================================
    // ✨ EFECTOS Y MEJORAS
    // ==============================================
    
    // Efecto al escribir
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.style.transform = "scale(1.01)";
        });
        input.addEventListener('blur', () => {
            input.parentElement.style.transform = "scale(1)";
        });
    });

    console.log('📥 Módulo Descargas cargado y listo');
});
