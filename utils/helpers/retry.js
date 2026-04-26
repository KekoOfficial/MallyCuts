async function retry(operacion, intentos = 3, delay = 1000) {
  try {
    return await operacion();
  } catch (err) {
    if (intentos > 1) {
      await new Promise(r => setTimeout(r, delay));
      return retry(operacion, intentos - 1, delay * 2);
    }
    throw err;
  }
}

module.exports = { retry };
