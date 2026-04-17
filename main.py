from flask import Flask, render_template, jsonify, request
import os, cortes, enviar

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_task():
    # Recibimos el archivo y el nombre
    file = request.files['video']
    serie_name = request.form['serie_name']
    
    # Guardamos el video en la carpeta uploads
    video_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(video_path)
    
    # Ejecutamos la lógica de cortes (usando el motor que ya tienes)
    # Aquí puedes llamar a tu función de cortes.py pasando 'video_path'
    resultado = motor_sakura_v10(video_path, serie_name)
    
    # Limpiamos el original después de procesar
    if os.path.exists(video_path): os.remove(video_path)
    
    return jsonify({"message": resultado})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
