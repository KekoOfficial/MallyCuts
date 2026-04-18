from flask import Flask, render_template, request, jsonify
import os
import threading
import queue
import subprocess
import time
from core.cortar import extraer_segmento
from core.enviar import despachar_a_telegram
import config

app = Flask(__name__)

# Carpetas
INPUT_FOLDER = "videos/input"
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_FOLDER, exist_ok=True)

PROCESANDO = False
cola = queue.Queue()

class MallyLogger:
    def __init__(self, nombre, total):
        self.nombre = nombre.strip().upper()
        self.total = total
        
    def exito(self, n):
        return (f"🎬 <b>{self.nombre}</b>\n"
                f"💎 <b>CAPÍTULO:</b> {n} / {self.total}\n"
                f"✅ <i>Contenido Verificado</i>\n"
                f"🔗 @MallySeries")

# --- HILOS DE ALTA VELOCIDAD ---
def productor(ruta_video, total_partes, log):
    """Corta super rapido y mete en cola"""
    for n in range(1, total_partes + 1):
        print(f"⚡ CORTANDO PARTE {n}/{total_partes}")
        path = extraer_segmento(ruta_video, n)
        if os.path.exists(path):
            cola.put({
                'n': n,
                'path': path,
                'caption': log.exito(n)
            })
    cola.put(None) # Fin

def consumidor():
    """Envia mientras el otro corta"""
    while True:
        item = cola.get()
        if item is None:
            break
        print(f"📤 ENVIANDO PARTE {item['n']}")
        ok = despachar_a_telegram(item['path'], item['caption'])
        if ok:
            print(f"✅ PARTE {item['n']} ENVIADA")
        if os.path.exists(item['path']):
            os.remove(item['path'])
        cola.task_done()

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
    
    ruta_entrada = os.path.join(INPUT_FOLDER, archivo.filename)
    archivo.save(ruta_entrada)
    
    PROCESANDO = True
    
    def trabajo_completo():
        global PROCESANDO
        
        # Calcular duracion y partes
        res = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', ruta_entrada
        ], capture_output=True, text=True)
        
        duracion = float(res.stdout)
        total_partes = int(duracion // config.CLIP_DURATION) + 1
        
        log = MallyLogger(titulo, total_partes)
        
        print(f"🔥 INICIANDO: {titulo} | PARTES: {total_partes}")
        
        # LANZAR EN PARALELO
        hilo1 = threading.Thread(target=productor, args=(ruta_entrada, total_partes, log))
        hilo2 = threading.Thread(target=consumidor)
        
        hilo1.start()
        hilo2.start()
        
        hilo1.join()
        hilo2.join()
        
        # Limpiar
        if os.path.exists(ruta_entrada):
            os.remove(ruta_entrada)
            
        PROCESANDO = False
        print("✅ MISION COMPLETADA")
    
    threading.Thread(target=trabajo_completo, daemon=True).start()
    
    return jsonify({"status": "ok", "mensaje": f"🚀 PROCESANDO {total_partes} PARTES EN MODO LUZ"})

if __name__ == "__main__":
    print("⚡ MALLYCUTS - MODO EXPRESS ACTIVADO ⚡")
    app.run(host="0.0.0.0", port=5000, debug=False)
