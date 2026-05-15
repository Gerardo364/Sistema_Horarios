import sqlite3
from tkinter import messagebox

class Sesion:
    usuario_actual = None
    rol_actual = None

    @classmethod
    def iniciar_sesion(cls, usuario, password):
        try:
            conn = sqlite3.connect('horarios_liceo.db')
            cursor = conn.cursor()
            cursor.execute("SELECT password, rol FROM usuarios WHERE usuario = ?", (usuario,))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                password_db, rol_db = resultado
                if password == password_db:
                    cls.usuario_actual = usuario
                    cls.rol_actual = rol_db
                    return True
            return False
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
            return False

    @classmethod
    def cerrar_sesion(cls):
        cls.usuario_actual = None
        cls.rol_actual = None

def requiere_admin(func):
    """ Middleware que verifica si el usuario es Administrativo """
    def envoltura(*args, **kwargs):
        if Sesion.rol_actual == "Administrativo":
            return func(*args, **kwargs)
        else:
            messagebox.showerror("Acceso Denegado", "Esta acción requiere permisos de Administrador.")
            return None 
    return envoltura