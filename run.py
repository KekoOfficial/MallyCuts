import os
import time
import telebot
import config
from flask import Flask, render_template

# --- CONFIGURACIÓN DE LA APP ---
# Asegúrate de que la carpeta 'templates' esté en el mismo directorio
app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN DE MANDO ---
ADMIN_ID = "8630490789"
bot = telebot.TeleBot(config.BOT_TOKEN)

# --- RUTAS DE FLASK ---
@app.route('/')
def index():
    # Esto cargará tu index.html que vimos en el código
    return render_template('index.html')

@app.route('/status')
def status():
    return "Umbrae Studio Core Online"

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    print("🚀 [CORE] Iniciando Servidor en Red Local...")
    print(f"📡 Accede desde tu navegador usando tu IP local en el puerto 8000")
    
    try:
        # Notificación básica de arranque al Admin
        bot.send_message(ADMIN_ID, "👑 <b>SISTEMA UMBRAE ACTIVO</b>\nRed local sincronizada.", parse_mode="HTML")
        
        # Ejecución normal: host 0.0.0.0 permite acceso desde otros dispositivos en la misma WiFi
        app.run(host="0.0.0.0", port=8000, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Apagando Servidor...")
