import customtkinter as ctk
from login_interfaz import LoginApp
from app import EduManageApp
from data_base import inicializar_db
from main import optimizar_conexiones_db
from PIL import Image
import sys
import os

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta del archivo, funciona tanto en desarrollo como
    cuando el programa está empaquetado con PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda los archivos en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class RootApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EduPlan - Liceo Armando Reverón")
        self.geometry("1100x700")

    # --- Configurar el icono de la ventana (barra de tareas) ---
        try:
            icono_path = resource_path("logo.png")
            if os.path.exists(icono_path):
                from PIL import ImageTk
                icon_image = ImageTk.PhotoImage(Image.open(icono_path))
                self.iconphoto(True, icon_image)
                # Guardar referencia para evitar que se pierda
                self.icono_referencia = icon_image
            else:
                print(f"Advertencia: No se encontró el icono en {icono_path}")
        except Exception as e:
            print(f"Error al cargar el icono: {e}")
        
        inicializar_db()
        optimizar_conexiones_db()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Contenedor principal: grid en la ventana (evita tamaño 0 al mezclar con hijos en grid)
        self.contenedor = ctk.CTkFrame(self)
        self.contenedor.grid(row=0, column=0, sticky="nsew")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.vistas = {}
        self.cambiar_vista("login_interfaz")

    def cambiar_vista(self, nombre_vista):
        # Limpiamos el contenedor
        for child in self.contenedor.winfo_children():
            child.destroy()

        # Instanciamos la clase según el nombre
        if nombre_vista == "login_interfaz":
            frame = LoginApp(self.contenedor, self)
        elif nombre_vista == "app":
            frame = EduManageApp(self.contenedor, self)
        
        frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = RootApp()
    app.mainloop()