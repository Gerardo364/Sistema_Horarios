from Materia import Materia
class Bloque:
    def __init__(self,dia,hora_inicio,hora_final, materia: Materia):
        self.dia=dia
        self.hora_inicio=hora_inicio
        self.hora_final=hora_final
        self.materia = materia 
        # self.horas = (hora_inicio,hora_final)
    
    def obtener_bloque(self):
        return f"{self.dia}: {self.hora_inicio}-{self.hora_final}"
    