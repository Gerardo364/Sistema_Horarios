class Materia:
    def __init__(self, nombre: str, id_seccion: str, horas_semanales: float = 0.0,dias_asignados=None):
        self.nombre = nombre
        self.id_seccion = id_seccion
        self.horas_semanales = horas_semanales
        self.horas_restantes = horas_semanales
        self.dias_asignados = dias_asignados if dias_asignados is not None else []
        self.bloques = []