from flask import Flask, render_template_string
import config

app = Flask(__name__)

HTML_UI = '''
<!DOCTYPE html>
<html>
<head>
    <title>CHROME MAGIC GOOD V2</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .terminal { border: 2px solid #0f0; padding: 30px; box-shadow: 0 0 15px #0f0; background: rgba(0,20,0,0.9); border-radius: 10px; text-align: center; }
        .glitch { font-size: 1.5rem; font-weight: bold; margin-bottom: 15px; text-transform: uppercase; }
        .stat { color: #fff; margin: 5px 0; font-size: 0.9rem; }
        .mode { color: #f0f; font-weight: bold; }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="glitch">[ CHROME MAGIC GOOD V2 ]</div>
        <div class="stat">> Estatus: <span style="color:#f0f">EJECUTANDO MOTOR</span></div>
        <div class="stat">> Escaneando Galería...</div>
        <div class="stat">> Modo: <span class="mode">Hyper-Velocity Automatizado</span></div>
        <hr style="border: 0.5px solid #0f0; margin: 15px 0;">
        <div style="font-size: 0.7rem; color: #888;">Desarrollado por Noa | Sistema Operativo MP</div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_UI)

def start_server():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
