from flask import Flask, render_template, request, jsonify
import os
import threading
import time
from core.cortar import extraer_segmento
from core.enviar import despachar_a_telegram
import config

app = Flask(__name__)

# Crear carpetas
os.makedirs("videos/input", exist_ok=True)
os.makedirs(config.TEMP_FOLDER, exist_ok=True)

PROCESANDO = False

class MallyLogger:
    def __init__(self, nombre, total):
        self.nombre = nombre.strip().upper()
        self.total = total
        
    def exito(self, n):
        return (f"🎬 <b>{self.nombre}</b>\n"
                f"💎 <b>CAPÍTULO:</b> {n} / {self.total}\n"
                f"✅ <i>Contenido Verificado</i>\n"
                f"🔗 @MallySeries")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    global PROCESANDO
    
    if PROCESANDO:
        return jsonify({"status": "ocupado", "mensaje": "⏳ Ya estoy trabajando..."})
    
    if "video" not in request.files:
        return jsonify({"status": "error", "mensaje": "Selecciona un video"})
    
    archivo = request.files["video"]
    titulo = request.form.get("titulo", "SIN TITULO")
    
    ruta_entrada = os.path.join("videos/input", archivo.filename)
    archivo.save(ruta_entrada)
    
    PROCESANDO = True
    
    def trabajo():
        global PROCESANDO
        
        # Calcular cuántas partes
        res = os.popen(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{ruta_entrada}"').read()
        duracion = float(res)
        total_partes = int(duracion // config.CLIP_DURATION) + 1
        
        log = MallyLogger(titulo, total_partes)
        
        print(f"🔥 Iniciando: {titulo} | Partes: {total_partes}")
        
        for i in range(1, total_partes + 1):
            print(f"✂️ Cortando parte {i}/{total_partes}")
            ruta_salida = extraer_segmento(ruta_entrada, i)
            
            if os.path.exists(ruta_salida):
                print(f"📤 Enviando parte {i}...")
                caption = log.exito(i)
                despachar_a_telegram(ruta_salida, caption)
                os.remove(ruta_salida)
        
        # Limpiar
        if os.path.exists(ruta_entrada):
            os.remove(ruta_entrada)
            
        PROCESANDO = False
        print("✅ MISION COMPLETADA")
    
    threading.Thread(target=trabajo, daemon=True).start()
    
    return jsonify({"status": "ok", "mensaje": f"🚀 Procesando {total_partes} partes..."})

if __name__ == "__main__":
    print("⚡ MALLYCUTS EXPRESS INICIADO")
    app.run(host="0.0.0.0", port=5000, debug=False)
