import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import sys
import subprocess
from auth import Sesion


# --- INTERFAZ GRÁFICA ---
class LoginApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tarjeta Central
        self.login_card = ctk.CTkFrame(self, width=380, height=580, fg_color="white", 
                                       corner_radius=15, border_width=1, border_color="#c1c6d4")
        self.login_card.grid(row=0, column=0, padx=20, pady=20)
        self.login_card.grid_propagate(False)
        self.login_card.grid_columnconfigure(0, weight=1)

        # Header 
        self.title_label = ctk.CTkLabel(
            self.login_card,
            text="Gestión de Horarios",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#004f96",
            wraplength=300,
            justify="center",
        )
        self.title_label.grid(row=0, column=0, pady=(50, 5))

        self.subtitle_label = ctk.CTkLabel(self.login_card, text="Liceo Armando Reverón",
                                           font=ctk.CTkFont(size=16), text_color="#414752")
        self.subtitle_label.grid(row=1, column=0, pady=(0, 40))

        # Inputs
        self.user_label = ctk.CTkLabel(self.login_card, text="Usuario", font=ctk.CTkFont(size=12, weight="bold"))
        self.user_label.grid(row=2, column=0, padx=40, sticky="w")
        
        self.user_entry = ctk.CTkEntry(self.login_card, placeholder_text="Enter your username", height=45)
        self.user_entry.grid(row=3, column=0, padx=40, pady=(5, 20), sticky="ew")

        self.pass_label = ctk.CTkLabel(self.login_card, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold"))
        self.pass_label.grid(row=4, column=0, padx=40, sticky="w")

        self.pass_entry = ctk.CTkEntry(self.login_card, placeholder_text="••••••••", show="*", height=45)
        self.pass_entry.grid(row=5, column=0, padx=40, pady=(5, 30), sticky="ew")

        # Botón de Ingreso (dentro del recuadro blanco)
        self.login_button = ctk.CTkButton(
            self.login_card,
            text="Sign In",
            command=self.intentar_ingreso,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.login_button.grid(row=6, column=0, padx=40, pady=(0, 50), sticky="ew")
        
        

    def intentar_ingreso(self):
        usuario = self.user_entry.get()
        password = self.pass_entry.get()
        if Sesion.iniciar_sesion(usuario, password):
            # Aquí le pedimos al controlador que cambie la vista
            self.controller.cambiar_vista("app")
        else:
            print("Error de login")
            
    def redireccionar(self):
        # Es vital cerrar esta ventana antes de abrir la otra
        self.withdraw() 
        try:
            subprocess.Popen([sys.executable, "app.py"])
            self.quit() # Finaliza el ciclo de esta app
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir app.py: {e}")
    
if __name__ == "__main__":
    # Asegúrate de que el usuario administrativo exista para probar
    conn = sqlite3.connect('horarios_liceo.db')
    conn.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT, password TEXT, rol TEXT)")
    # Si la tabla está vacía, insertamos uno de prueba
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        conn.execute("INSERT INTO usuarios VALUES ('admin', '1234', 'Administrativo')")
        conn.commit()
    conn.close()

    app = LoginApp()
    app.mainloop()