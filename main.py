import threading
import time
import server
import bot_mally

def loop_bot():
    print(">> Motor Noa activado...")
    while True:
        try:
            bot_mally.procesar_ciclo()
        except Exception as e:
            print(f">> Alerta de Sistema: {e}")
        time.sleep(10)

if __name__ == "__main__":
    # Servidor de monitoreo visual
    threading.Thread(target=server.start_server, daemon=True).start()
    
    # Motor de procesamiento
    loop_bot()
