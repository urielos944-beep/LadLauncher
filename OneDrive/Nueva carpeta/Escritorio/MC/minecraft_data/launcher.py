import minecraft_launcher_lib
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

# Configuración de carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
minecraft_directory = os.path.join(BASE_DIR, ".minecraft_custom")

class MinecraftLauncherPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Ultra Launcher - Todas las Versiones")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- UI ---
        tk.Label(root, text="MINECRAFT LAUNCHER PRO", font=("Impact", 24), fg="#00ff00", bg="#1e1e1e").pack(pady=10)

        # Selección de Usuario
        tk.Label(root, text="Nombre de Usuario:", fg="white", bg="#1e1e1e").pack()
        self.user_entry = tk.Entry(root, width=30); self.user_entry.insert(0, "Gamer_Alpha"); self.user_entry.pack(pady=5)

        # Lista de Versiones
        tk.Label(root, text="Selecciona la Versión (Alpha, Beta, Release):", fg="white", bg="#1e1e1e").pack()
        self.version_combo = ttk.Combobox(root, width=40, state="readonly")
        self.version_combo.pack(pady=5)
        
        # Botón Cargar Versiones
        self.btn_load = tk.Button(root, text="Cargar Lista de Versiones", command=self.cargar_versiones, bg="#3498db", fg="white")
        self.btn_load.pack(pady=5)

        # Consola de logs
        self.log_text = tk.Text(root, height=10, width=70, bg="black", fg="#00ff00", font=("Consolas", 8))
        self.log_text.pack(pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(root, length=500, mode='determinate')
        self.progress.pack(pady=10)

        # Botón Jugar
        self.btn_play = tk.Button(root, text="¡INSTALAR Y JUGAR!", command=self.iniciar_hilo, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), width=20)
        self.btn_play.pack(pady=10)

    def log(self, mensaje):
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)

    def cargar_versiones(self):
        self.log("Obteniendo versiones desde Mojang...")
        try:
            # Esto descarga la lista completa: Alpha, Beta, Snapshots y Releases
            versiones = minecraft_launcher_lib.utils.get_version_list()
            lista_nombres = [v['id'] for v in versiones]
            self.version_combo['values'] = lista_nombres
            self.version_combo.current(0)
            self.log(f"Se cargaron {len(lista_nombres)} versiones con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")

    def iniciar_hilo(self):
        version = self.version_combo.get()
        usuario = self.user_entry.get()
        if not version:
            return messagebox.showwarning("Aviso", "Primero carga y selecciona una versión")
        
        self.btn_play.config(state="disabled")
        threading.Thread(target=self.instalar_y_lanzar, args=(version, usuario), daemon=True).start()

    def instalar_y_lanzar(self, version, usuario):
        def set_status(t): self.log(t)
        def set_progress(v): self.progress["value"] = v
        def set_max(m): self.progress["maximum"] = m

        callback = {"setStatus": set_status, "setProgress": set_progress, "setMax": set_max}

        try:
            self.log(f"Iniciando descarga de {version}...")
            # Descarga el motor, assets y librerías
            minecraft_launcher_lib.install.install_minecraft_version(version, minecraft_directory, callback=callback)
            
            options = {
                "username": usuario,
                "uuid": "",
                "token": "",
                "jvmArguments": ["-Xmx2G", "-Xms2G"] # 2GB de RAM
            }
            
            self.log("Construyendo comando de lanzamiento...")
            comando = minecraft_launcher_lib.command.get_minecraft_command(version, minecraft_directory, options)
            
            self.log("¡Lanzando! El launcher se cerrará o quedará en espera.")
            subprocess.run(comando)
            
        except Exception as e:
            self.log(f"ERROR CRÍTICO: {e}")
        finally:
            self.btn_play.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLauncherPro(root)
    root.mainloop()