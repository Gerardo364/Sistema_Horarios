from Bloque import Bloque  

class Horario:
    def __init__(self, ID: str, bloques: list[Bloque] = None):
        self.ID = ID
        self.bloques = bloques if bloques is not None else []
   
   #No se si es necesario xd
    def mostrar(self):
        pass