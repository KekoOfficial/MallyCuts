import server, main, threading, config
from flask import request

@server.app.route('/process', methods=['POST'])
def handle_process():
    link = request.form.get('link')
    titulo = request.form.get('titulo')
    
    threading.Thread(target=main.motor_descarga_y_corte, args=(link, titulo)).start()
    return "<h1>🚀 Descarga iniciada en segundo plano...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    server.app.run(host='0.0.0.0', port=config.PORT)
