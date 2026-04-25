// ==============================================
// 🎮 CONTROLADOR PRINCIPAL - MALLYCUTS
// ==============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Controlador cargado y listo');

    // ==============================================
    // 🔄 FUNCIONES GENERALES
    // ==============================================
    
    function mostrarMensaje(texto, tipo = 'info') {
        const resultado = document.getElementById('resultado');
        resultado.className = `resultado ${tipo}`;
        resultado.textContent = texto;
        resultado.style.display = 'block';
    }

    function desactivarBoton(boton, texto = 'PROCESANDO...') {
        boton.disabled = true;
        boton.textContent = texto;
    }

    function activarBoton(boton, texto) {
        boton.disabled = false;
        boton.textContent = texto;
    }

    // ==============================================
    // 🎛️ CAMBIO DE PESTAÑAS
    // ==============================================
    
    const btnArchivo = document.getElementById('btnArchivo');
    const btnEnlace = document.getElementById('btnEnlace');
    const seccionArchivo = document.getElementById('seccionArchivo');
    const seccionEnlace = document.getElementById('seccionEnlace');

    btnArchivo.addEventListener('click', () => {
        seccionArchivo.style.display = 'block';
        seccionEnlace.style.display = 'none';
        btnArchivo.classList.add('activo');
        btnEnlace.classList.remove('activo');
    });

    btnEnlace.addEventListener('click', () => {
        seccionArchivo.style.display = 'none';
        seccionEnlace.style.display = 'block';
        btnArchivo.classList.remove('activo');
        btnEnlace.classList.add('activo');
    });

    // ==============================================
    // 📂 SELECCIONAR ARCHIVO
    // ==============================================
    
    const inputFile = document.getElementById('video');
    const fileText = document.getElementById('file-text');

    if(inputFile) {
        inputFile.addEventListener('change', function(e) {
            if(e.target.files.length > 0) {
                fileText.textContent = e.target.files[0].name;
            } else {
                fileText.textContent = 'Click para seleccionar un video';
            }
        });
    }

    // ==============================================
    // 🚀 FORMULARIO SUBIR ARCHIVO
    // ==============================================
    
    const formArchivo = document.getElementById('formularioArchivo');
    
    if(formArchivo) {
        formArchivo.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = e.target.querySelector('button[type="submit"]');
            desactivarBoton(btn, '⏳ SUBIENDO...');

            try {
                // 1. SUBIR EL ARCHIVO
                const formData = new FormData(formArchivo);
                
                const resUpload = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const dataUpload = await resUpload.json();

                if(dataUpload.status !== 'ok') {
                    throw new Error(dataUpload.mensaje || 'Error al subir');
                }

                mostrarMensaje('📄 Archivo subido. Iniciando proceso...', 'ok');
                
                // 2. ENVIAR A PROCESAR
                const resProceso = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        titulo: dataUpload.titulo,
                        archivo: dataUpload.archivo
                    })
                });

                const dataProceso = await resProceso.json();
                
                if(dataProceso.status === 'ok') {
                    mostrarMensaje('✅ ' + dataProceso.mensaje, 'ok');
                } else {
                    throw new Error(dataProceso.mensaje);
                }

                activarBoton(btn, '🚀 INICIAR PROCESO');

            } catch (error) {
                mostrarMensaje('❌ Error: ' + error.message, 'error');
                activarBoton(btn, '🚀 INICIAR PROCESO');
                console.error(error);
            }
        });
    }

    console.log('🎮 MallyCuts listo para usar');
});
