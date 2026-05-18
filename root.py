import customtkinter as ctk
from login_interfaz import LoginApp
from app import EduManageApp
from data_base import inicializar_db

class RootApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EduManage - Liceo Armando Reverón")
        self.geometry("1100x700")

        
        inicializar_db()
        
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