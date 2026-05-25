from Docente import Docente
from Seccion import Seccion
from Horario import Horario
from Bloque import Bloque 
from Materia import Materia
from Exportar import exportar_a_pdf
        
import random

class SistemaHorarios:
    MATERIAS_FUERTES = {"Biología", "Química", "Matemática"}
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
    
    #
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
        
        # 1. Estructuras de búsqueda rápida (O(1)) para el estado
        self._docentes_ocupados = set()  # (dia, bloque, cedula)
        self._secciones_ocupadas = set() # (dia, bloque, id_seccion)
        self._materias_hoy = set()       # (dia, id_seccion, materia.nombre)
        
        self._fuertes_seccion = {}       # (dia, id_seccion) -> cantidad
        self._fuertes_docente = {}       # (dia, cedula) -> cantidad
        self._ultimo_bloque = {}         # (dia, bloque, cedula) -> id_seccion

        # 2. PREPARACIÓN ("Las rocas grandes primero")
        # Desglosamos las materias en "bloques a asignar" (1 bloque = 2 horas)
        tareas = []
        for docente in self.docentes:
            for materia in docente.materias:
                # Restauramos horas para evitar bugs si se genera varias veces
                materia.horas_restantes = materia.horas_semanales 
                bloques_necesarios = int(materia.horas_semanales // 2)
                for _ in range(bloques_necesarios):
                    tareas.append((docente, materia))
        
        # Al ordenar de mayor a menor, las materias de 6 horas se asignan primero
        tareas.sort(key=lambda t: t[1].horas_semanales, reverse=True)

        # 3. INICIAR RECURSIVIDAD
        exito = self._asignar_backtrack(tareas, 0)
        
        if not exito:
            print("Aviso: El algoritmo hizo su mejor esfuerzo, pero hay choques que impiden un horario 100% perfecto.")

    def _asignar_backtrack(self, tareas, indice):
        """Función recursiva principal de Backtracking"""
        # Caso base: Si el índice llega al final de la lista, asignamos todo
        if indice == len(tareas):
            return True
            
        docente, materia = tareas[indice]
        
        for dia in self.dias:
            for bloque in self.bloques:
                if self._es_valido(dia, bloque, docente, materia):
                    
                    # 1. HACER MOVIMIENTO (Guardar estado)
                    self._registrar_estado(dia, bloque, docente, materia, colocar=True)
                    
                    # 2. EXPLORAR (Llamada recursiva a la siguiente materia)
                    if self._asignar_backtrack(tareas, indice + 1):
                        return True
                        
                    # 3. DESHACER MOVIMIENTO (Backtrack: si no funcionó, quitamos y probamos otro)
                    self._registrar_estado(dia, bloque, docente, materia, colocar=False)
                    
        # Si probó todos los días y bloques y nada funcionó, retrocede al nivel anterior
        return False

    def _es_valido(self, dia, bloque, docente, materia):
        """Aísla y limpia todas las reglas de negocio (ifs)"""
        # Regla 1: Día libre del docente
        if docente.dia_libre and docente.dia_libre != "Ninguno" and dia.lower() == docente.dia_libre.lower():
            return False
            
        # Regla 2: Días específicos solicitados para la materia
        if hasattr(materia, 'dias_asignados') and materia.dias_asignados:
            if dia.capitalize() not in materia.dias_asignados:
                return False
                
        # Regla 3: Choques básicos (Docente o sección ya ocupados)
        if (dia, bloque, docente.cedula) in self._docentes_ocupados: return False
        if (dia, bloque, materia.id_seccion) in self._secciones_ocupadas: return False
        
        # Regla 4: No bloques dobles (solo 1 vez al día por materia)
        if (dia, materia.id_seccion, materia.nombre) in self._materias_hoy: return False
        
        # Regla 5: Control de materias fuertes (Máx 2 por día)
        if materia.nombre in self.MATERIAS_FUERTES:
            if self._fuertes_seccion.get((dia, materia.id_seccion), 0) >= 2: return False
            if self._fuertes_docente.get((dia, docente.cedula), 0) >= 2: return False
            
        # Regla 6: Restricción de separación (Evitar que el profesor salte de sección sin receso)
        idx = self.bloques.index(bloque)
        if idx > 0:
            bloque_prev = self.bloques[idx - 1]
            sec_prev = self._ultimo_bloque.get((dia, bloque_prev, docente.cedula))
            if sec_prev and sec_prev != materia.id_seccion: return False
            
        if idx < len(self.bloques) - 1:
            bloque_next = self.bloques[idx + 1]
            sec_next = self._ultimo_bloque.get((dia, bloque_next, docente.cedula))
            if sec_next and sec_next != materia.id_seccion: return False
                
        return True

    def _registrar_estado(self, dia, bloque, docente, materia, colocar):
        """Manejador centralizado para actualizar (o limpiar) el estado global"""
        es_fuerte = materia.nombre in self.MATERIAS_FUERTES
        
        if colocar:
            self.horario_maestro[(dia, bloque, materia.id_seccion)] = {
                "materia": materia.nombre,
                "docente": docente.nombre,
                "cedula": docente.cedula
            }
            self._docentes_ocupados.add((dia, bloque, docente.cedula))
            self._secciones_ocupadas.add((dia, bloque, materia.id_seccion))
            self._materias_hoy.add((dia, materia.id_seccion, materia.nombre))
            self._ultimo_bloque[(dia, bloque, docente.cedula)] = materia.id_seccion
            
            if es_fuerte:
                self._fuertes_seccion[(dia, materia.id_seccion)] = self._fuertes_seccion.get((dia, materia.id_seccion), 0) + 1
                self._fuertes_docente[(dia, docente.cedula)] = self._fuertes_docente.get((dia, docente.cedula), 0) + 1
            materia.horas_restantes -= 2
            
        else: # Reversa todo en caso de Backtrack
            del self.horario_maestro[(dia, bloque, materia.id_seccion)]
            self._docentes_ocupados.remove((dia, bloque, docente.cedula))
            self._secciones_ocupadas.remove((dia, bloque, materia.id_seccion))
            self._materias_hoy.remove((dia, materia.id_seccion, materia.nombre))
            del self._ultimo_bloque[(dia, bloque, docente.cedula)]
            
            if es_fuerte:
                self._fuertes_seccion[(dia, materia.id_seccion)] -= 1
                self._fuertes_docente[(dia, docente.cedula)] -= 1
            materia.horas_restantes += 2
    
    def generar_y_persistir(self):
        from data_base import guardar_horario_maestro
        self.generar_horario()
        
        if not self.horario_maestro:
            return False, "No se pudo generar el horario. Verifique las horas y días asignados."
        
        exito_bd = guardar_horario_maestro(self.horario_maestro)
        if not exito_bd:
            return False, "El horario se generó pero no se pudo guardar en la base de datos."
        
        try:
            exportar_a_pdf(self.horario_maestro, nombre_archivo="horario_liceo.pdf")
            return True, "Horario generado, guardado en BD y exportado a PDF correctamente."
        except Exception as e:
            return False, f"Horario guardado en BD pero falló la exportación a PDF: {e}"