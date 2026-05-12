import sqlite3

class Sesion:
    usuario_actual = None
    rol_actual = None

    @classmethod
    def iniciar_sesion(cls, usuario, password):
        try:
            conn = sqlite3.connect('horarios_liceo.db')
            cursor = conn.cursor()
            
            # Buscamos al usuario y su clave en la tabla
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
        except sqlite3.Error:
            return False

def requiere_admin(func):
    """
    Middleware que verifica el rol antes de ejecutar una función.
    Si el rol no es 'Administrativo', bloquea la ejecución.
    """
    def envoltura(*args, **kwargs):
        if Sesion.rol_actual == "Administrativo":
            return func(*args, **kwargs)
        else:
            print("\n ACCESO DENEGADO: Solo el personal Administrativo puede realizar esta acción.")
            return None 
    return envoltura