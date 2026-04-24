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
    const fileLabel = document.getElementById('file-label');

    if(inputFile) {
        inputFile.addEventListener('change', function(e) {
            if(e.target.files.length > 0) {
                fileLabel.textContent = e.target.files[0].name;
            } else {
                fileLabel.textContent = 'Ningún archivo seleccionado';
            }
        });
    }

    // ==============================================
    // 🚀 FORMULARIO: SUBIR ARCHIVO
    // Llama a: /upload y luego /procesar
    // ==============================================
    
    const formArchivo = document.getElementById('formularioArchivo');
    
    if(formArchivo) {
        formArchivo.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = e.target.querySelector('button[type="submit"]');
            desactivarBoton(btn, '⏳ SUBIENDO...');

            try {
                // 1. Subir el archivo (usando el router upload)
                const formData = new FormData(formArchivo);
                
                const resUpload = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const dataUpload = await resUpload.json();

                if(dataUpload.status !== 'ok') {
                    throw new Error(dataUpload.mensaje || 'Error al subir');
                }

                mostrarMensaje('📄 Archivo subido correctamente. Iniciando corte...', 'ok');
                
                // 2. Una vez subido, llamar al proceso completo
                activarBoton(btn, '🚀 INICIAR PROCESO');

                // Aquí conectamos con el proceso principal
                const resProceso = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        titulo: dataUpload.titulo,
                        archivo: dataUpload.archivo
                    })
                });

                const dataProceso = await resProceso.json();
                mostrarMensaje(dataProceso.mensaje, dataProceso.status);

            } catch (error) {
                mostrarMensaje('❌ Error: ' + error.message, 'error');
                activarBoton(btn, '🚀 INICIAR PROCESO');
            }
        });
    }

    // ==============================================
    // 🔗 FORMULARIO: ENLACE / LINK
    // Llama a: /enlaces/procesar
    // ==============================================
    
    const formEnlace = document.getElementById('formularioEnlace');

    if(formEnlace) {
        formEnlace.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = e.target.querySelector('button[type="submit"]');
            desactivarBoton(btn, '⏳ DESCARGANDO...');

            try {
                const datos = {
                    titulo: document.getElementById('tituloEnlace').value,
                    url: document.getElementById('url').value
                };

                // Llamamos al router de enlaces
                const res = await fetch('/enlaces/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(datos)
                });

                const data = await res.json();
                mostrarMensaje(data.mensaje, data.status);
                activarBoton(btn, '🚀 DESCARGAR Y PROCESAR');

            } catch (error) {
                mostrarMensaje('❌ Error: ' + error.message, 'error');
                activarBoton(btn, '🚀 DESCARGAR Y PROCESAR');
            }
        });
    }

    // ==============================================
    // ⚙️ OBTENER CONFIGURACIÓN AL INICIAR
    // ==============================================
    
    async function cargarConfig() {
        try {
            const res = await fetch('/config');
            const config = await res.json();
            console.log('⚙️ Configuración cargada:', config);
        } catch (e) {
            console.log('ℹ️ Sistema listo');
        }
    }

    cargarConfig();

    console.log('🎮 Controlador MallyCuts v2.0 activo');
});
