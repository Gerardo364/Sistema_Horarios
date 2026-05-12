from Horario import Horario
from Materia import Materia

class Docente:
    def __init__(self, nombre: str, cedula: str, dia_libre: str="", materias=None) -> None:
        self.nombre = nombre
        self.cedula = cedula
        self.dia_libre = dia_libre
        self.materias = materias if materias is not None else []
        self.horario = None
        
    def asignar_horario(self, horario: Horario):
        try:
            if not isinstance(horario, Horario):
                raise TypeError
            self.horario = horario
            return f"Horario fue asignado exitosamente"
        except TypeError:
            return f"Error: se esperaba Horario, no {type(horario).__name__}"
        except Exception as e:
            return f"Error inesperado: {e}"

    def agregar_materia(self, materia: Materia):
        try:
            if not isinstance(materia, Materia):
                raise TypeError
            self.materias.append(materia)
            return f"Materia fue agregada exitosamente"
        except TypeError:
            return f"Error: se esperaba Materia, no {type(materia).__name__}"
        except Exception as e:
            return f"Error inesperado: {e}"
        
    def eliminar_materia(self, materia):  # prototipo de lo que podria hacer
        try:
            if not isinstance(materia, Materia):
                raise TypeError
            
            if not self.buscar_materia(materia):                       
                return f"Materia no encontrada"
            
            self.materias.remove(materia)
            return f"Materia eliminada"     
        
        except TypeError:
            return f"Error: se esperaba Materia, no {type(materia).__name__}"
        except Exception as e:
            return f"Error inesperado: {e}"
        
        
    def buscar_materia(self, materia): # prototipo de lo que podria hacer
        try:
            if not isinstance(materia, Materia):
                raise TypeError()
            
            if materia in self.materias:
                return True            
            return False
        
        except TypeError:
            return f"Error: se esperaba Materia, no {type(materia).__name__}"
        except Exception as e:
            return f"Error inesperado: {e}"
    
    