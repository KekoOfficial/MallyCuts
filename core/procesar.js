// Importas la función de envío que tendrás en el otro archivo
const { enviarParte } = require('./enviar2.js');
const fs = require('fs');

// --- TU PROCESO ACTUAL ---
console.log("⚡ PROCESANDO PARTE 1/1");

// Supongamos que aquí tienes el código que corta el archivo
let parte1 = "./parte1.mp4"; // Ruta del archivo que ya cortaste

// Verificas que el archivo exista realmente
if (fs.existsSync(parte1)) {
    console.log("✅ Parte 1 cortada correctamente");
    console.log("📤 ENVIANDO PARTE 1");

    // Llamas a la función de envío, le pasas el archivo y los datos
    enviarParte(parte1, "Parte 1")
        .then(() => {
            console.log("✅ ¡TODO FINALIZADO CORRECTAMENTE!");
            console.log("==================================================");
            
            // AQUÍ MÁS TARDE PODRÁS LLAMAR A ENVIAR LA PARTE 2, CUANDO ESTÉ LISTA
            // enviarParte("./parte2.mp4", "Parte 2");
        })
        .catch(err => {
            console.log("⚠️ PARTE 1 NO SE PUDO ENVIAR");
            console.error("Error detallado:", err);
        });

} else {
    console.log("❌ Error: El archivo de la parte 1 no existe");
}
