import threading
import time
import server
import bot_mally

def loop_bot():
    print("🚀 Motor Mally activado...")
    while True:
        try:
            bot_mally.procesar_ciclo()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    # Iniciar interfaz visual en hilo secundario
    web_thread = threading.Thread(target=server.start_server)
    web_thread.daemon = True
    web_thread.start()
    
    # Iniciar bot en hilo principal
    loop_bot()
