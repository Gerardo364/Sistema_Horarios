from Docente import Docente
from Seccion import Seccion
from Horario import Horario
from Bloque import Bloque 
from Materia import Materia

import random

class SistemaHorarios:
    def __init__(self):
        self.docentes = []
        self.dias = ("Lunes", "Martes", "Miercoles", "Jueves", "Viernes")
        self.bloques = ("8:00-9:10","9:20-10:30","10:35-11:45", "11:50-13:00")
        self.horario_maestro = {}

    def agregar_docente(self, docente: Docente):
        try:
            if not isinstance(docente, Docente):
                raise TypeError()
            self.docentes.append(docente)
            return f"Materia fue agregada exitosamente"
        except TypeError:
            return f"Error: se esperaba Docente, no {type(docente).__name__}"
        except Exception as e:
            return f"Error inesperado: {e}"
    
    
    def inicializar_bloques_del_liceo(self):
        self.lista_objetos_bloques = []
        
        for dia in self.dias:
            for bloque_texto in self.bloques: 
                inicio, fin = bloque_texto.split("-")
                nuevo_bloque = Bloque(dia, inicio, fin, Materia('',''))
                self.lista_objetos_bloques.append(nuevo_bloque)
        
        random.shuffle(self.lista_objetos_bloques)

    def generar_horario(self):   
        self.horario_maestro = {}
        docente_ocupado = []
        seccion_ocupada = []
        materia_dada_hoy = []
        ultimo_bloque_docente = {}

        for dia in self.dias:
            materia_dada_hoy = []
            for bloque in self.bloques:
                indice_bloque_actual = self.bloques.index(bloque)
                
                for docente in self.docentes:
                    if dia.lower() == docente.dia_libre.lower():
                        continue
                    
                    bloque_anterior = self.bloques[indice_bloque_actual - 1] if indice_bloque_actual > 0 else None
                    ultima_seccion = ultimo_bloque_docente.get((docente.cedula, dia, bloque_anterior))

                    for materia in docente.materias:
                        if materia.horas_restantes <= 0: 
                            continue

                        # --- RESTRICCIÓN DE SEPARACIÓN (Lo que pediste) ---
                        if ultima_seccion and ultima_seccion != materia.id_seccion:
                            continue 

                        # --- RESTRICCIÓN DE DÍAS ASIGNADOS (Lo que pidió el Admin) ---
                        if hasattr(materia, 'dias_asignados') and materia.dias_asignados:
                            if dia.capitalize() not in materia.dias_asignados:
                                continue

                        # --- VALIDACIONES DE DISPONIBILIDAD ---
                        if (dia, bloque, docente.cedula) in docente_ocupado: 
                            continue
                        if (dia, bloque, materia.id_seccion) in seccion_ocupada: 
                            continue
                        if (dia, materia.id_seccion, materia.nombre) in materia_dada_hoy:
                            continue
                        
                        # --- ASIGNACIÓN ÚNICA (Solo una vez) ---
                        self.horario_maestro[(dia, bloque, materia.id_seccion)] = {
                            "materia": materia.nombre,
                            "docente": docente.nombre,
                            "cedula": docente.cedula
                        }
                
                        docente_ocupado.append((dia, bloque, docente.cedula))
                        seccion_ocupada.append((dia, bloque, materia.id_seccion))
                        materia_dada_hoy.append((dia, materia.id_seccion, materia.nombre))
                        
                        # Guardamos la sección para el siguiente bloque
                        ultimo_bloque_docente[(docente.cedula, dia, bloque)] = materia.id_seccion
                        
                        materia.horas_restantes -= 2
                        break