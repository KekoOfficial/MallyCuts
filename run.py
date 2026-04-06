import subprocess
import os

# Asegura que las carpetas existan antes de empezar
os.makedirs("videos_galeria", exist_ok=True)
os.makedirs("mally_studio_segments", exist_ok=True)

print("--- INICIANDO SISTEMA OPERATIVO MP ---")
subprocess.run(["python", "main.py"])
