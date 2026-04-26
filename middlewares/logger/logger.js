const colores = {
  reset: "\x1b[0m",
  verde: "\x1b[32m",
  rojo: "\x1b[31m",
  amarillo: "\x1b[33m",
  azul: "\x1b[34m",
  cyan: "\x1b[36m"
};

const fecha = () => new Date().toLocaleString();

module.exports = {
  separador: () => console.log("=".repeat(70)),
  inicio: txt => console.log(`${colores.cyan}[${fecha()}] 🚀 ${txt}${colores.reset}`),
  exito: txt => console.log(`${colores.verde}[${fecha()}] ✅ ${txt}${colores.reset}`),
  error: (txt, err) => {
    console.log(`${colores.rojo}[${fecha()}] 💥 ${txt}${colores.reset}`);
    if (err) console.log(err);
  },
  info: txt => console.log(`${colores.azul}[${fecha()}] ℹ️  ${txt}${colores.reset}`),
  detalle: txt => console.log(`${colores.amarillo}[${fecha()}] 🔍 ${txt}${colores.reset}`),
};
