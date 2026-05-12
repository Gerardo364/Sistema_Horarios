from Horario import Horario
from Materia import Materia

class Seccion:
    def __init__(self,letra: str ,grado:int,materias: list[Materia]):
        self.letra=letra
        self.grado=grado
        self.id_seccion = f"{grado}{letra}"
        self.materias = materias
        self.horario = None
    
    def __str__(self):
        return f"Sección {self.grado}° '{self.letra}'"
    
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
        
