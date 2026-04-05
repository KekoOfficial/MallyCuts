import server, main, threading, config
from flask import request

@server.app.route('/run', methods=['POST'])
def handle():
    t = request.form.get('titulo')
    l = request.form.get('link')
    threading.Thread(target=main.motor_principal, args=(l, t)).start()
    return "<h1>🚀 Descarga iniciada...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    print(f"🔥 Sistema Mally Pro en línea: http://localhost:{config.PORT}")
    server.app.run(host='0.0.0.0', port=config.PORT)
