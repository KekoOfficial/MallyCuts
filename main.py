from flask import Flask, render_template, request, jsonify
import os
import threading
from core.cortar import cortar_video
from core.enviar import enviar_video

app = Flask(__name__)

# Rutas
INPUT_FOLDER = "videos/input"
OUTPUT_FOLDER = "videos/output"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PROCESANDO = False

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
    titulo = request.form.get("titulo", "Sin Titulo")
    
    if archivo.filename == "":
        return jsonify({"status": "error", "mensaje": "Archivo vacío"})
    
    # Guardar archivo
    ruta_entrada = os.path.join(INPUT_FOLDER, archivo.filename)
    archivo.save(ruta_entrada)
    
    # Ruta de salida
    nombre_salida = f"cortado_{archivo.filename}"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)
    
    print(f"📥 Recibido: {titulo}")
    PROCESANDO = True
    
    def trabajo():
        global PROCESANDO
        # ✂️ Cortar y escalar a 1080p
        ok = cortar_video(ruta_entrada, ruta_salida)
        
        if ok:
            print("✅ Video listo")
            # 📤 Enviar a Telegram
            enviar_video(ruta_salida, titulo)
            print("📤 Enviado a Telegram")
        else:
            print("❌ Falló el proceso")
            
        # Limpiar
        try: os.remove(ruta_entrada)
        except: pass
        PROCESANDO = False
    
    threading.Thread(target=trabajo, daemon=True).start()
    
    return jsonify({"status": "ok", "mensaje": "🚀 Procesando y enviando..."})

if __name__ == "__main__":
    print("⚡ MallyCuts MINI PRO iniciado")
    print("🌐 Abre: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
