import server, main, threading, os, config

@server.app.route('/upload', methods=['POST'])
def handle_upload():
    video_file = server.request.files['file']
    titulo = server.request.form.get('titulo')
    
    save_path = "entrada_temp.mp4"
    video_file.save(save_path)
    
    # Lanzamos el motor en un hilo independiente para no bloquear la web
    threading.Thread(target=main.motor_procesamiento, args=(save_path, titulo)).start()
    
    return "<h1>🚀 Procesando en segundo plano...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    print(f"🔥 MALLY SERIES PRO activo en el puerto {config.PORT}")
    server.app.run(host='0.0.0.0', port=config.PORT, debug=False)
