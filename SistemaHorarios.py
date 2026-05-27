from Docente import Docente
from Seccion import Seccion
from Horario import Horario
from Bloque import Bloque 
from Materia import Materia
from Exportar import exportar_a_pdf
import copy 
import random

class SistemaHorarios:
    MATERIAS_FUERTES = {"Biología", "Química", "Matemática"}
    def __init__(self):
        self.docentes = []
        self.dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
        self.bloques = ["8:00-9:10","9:20-10:30","10:35-11:45", "11:50-13:00"]
        self.horario_maestro = {}
        self.progress_callback = None
        self.materias_no_asignadas = []
    
    def set_progress_callback(self, callback):
        """Establece función para reportar progreso"""
        self.progress_callback = callback
            
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
    def diagnosticar_factibilidad(self):
        """
        Verifica si es posible generar un horario antes de intentarlo.
        IMPORTANTE: Cada bloque = 2 horas.
        Capacidad: 4 bloques/día × 5 días = 20 bloques/semana = 40 horas/semana
        """
        problemas = []
        advertencias = []
        
        # Capacidades correctas
        BLOQUES_POR_DIA = len(self.bloques)  # 4 bloques
        DIAS = len(self.dias)  # 5 días
        HORAS_POR_BLOQUE = 2
        
        MAX_BLOQUES_SEMANA = BLOQUES_POR_DIA * DIAS  # 4 × 5 = 20 bloques
        MAX_HORAS_SEMANA = MAX_BLOQUES_SEMANA * HORAS_POR_BLOQUE  # 20 × 2 = 40 horas
        
        for docente in self.docentes:
            horas_totales = sum(m.horas_semanales for m in docente.materias)
            
            # Calcular días disponibles considerando día libre
            dias_disponibles = DIAS
            if docente.dia_libre and docente.dia_libre != "Ninguno" and docente.dia_libre in self.dias:
                dias_disponibles = DIAS - 1
            
            max_bloques_docente = BLOQUES_POR_DIA * dias_disponibles
            max_horas_docente = max_bloques_docente * HORAS_POR_BLOQUE
            
            if horas_totales > max_horas_docente:
                problemas.append({
                    "nombre": docente.nombre,
                    "horas": horas_totales,
                    "maximo": max_horas_docente,
                    "dias_disponibles": dias_disponibles,
                    "exceso": horas_totales - max_horas_docente
                })
            elif horas_totales > max_horas_docente * 0.8:
                advertencias.append({
                    "nombre": docente.nombre,
                    "horas": horas_totales,
                    "maximo": max_horas_docente,
                    "porcentaje": (horas_totales / max_horas_docente) * 100
                })
        
        return problemas, advertencias
    
    def generar_horario(self, max_intentos=3):
        """
        Algoritmo greedy con reintentos para asignación de horarios.
        """
        self.materias_no_asignadas = []
        
        # Diagnóstico inicial
        problemas, advertencias = self.diagnosticar_factibilidad()
        
        if problemas:
            print("\nPROBLEMAS DETECTADOS:")
            for p in problemas:
                print(f"   {p['nombre']}: {p['horas']}h > {p['maximo']}h (exceso de {p['exceso']}h)")
                print(f"      Días disponibles: {p['dias_disponibles']}")
            if self.progress_callback:
                self.progress_callback(100, f"Error: {len(problemas)} docente(s) con sobrecarga")
            return False
        
        if advertencias and self.progress_callback:
            self.progress_callback(5, f"Advertencia: {len(advertencias)} docente(s) cerca del límite")
        
        for intento in range(max_intentos):
            if self.progress_callback:
                self.progress_callback(intento * 10, f"Intento {intento + 1} de {max_intentos}...")
            
            # Limpiar horario anterior
            self.horario_maestro = {}
            
            # Estructuras para trackear ocupación
            docente_ocupado = set()
            seccion_ocupada = set()
            materia_por_dia = set()
            fuertes_por_seccion = {}
            fuertes_por_docente = {}
            
            # Preparar lista de materias a asignar
            tareas = []
            for docente in self.docentes:
                for materia in docente.materias:
                    materia.horas_restantes = materia.horas_semanales
                    # Cada bloque = 2 horas
                    bloques_necesarios = int(materia.horas_semanales / 2)
                    if materia.horas_semanales % 2 != 0:
                        bloques_necesarios += 1
                    
                    for i in range(bloques_necesarios):
                        tareas.append({
                            'docente': docente,
                            'materia': materia,
                            'bloque_id': i + 1,
                            'total_bloques': bloques_necesarios
                        })
            
            if not tareas:
                if self.progress_callback:
                    self.progress_callback(100, "No hay materias para asignar")
                return False
            
            # Ordenar tareas: más horas primero
            tareas.sort(key=lambda t: (
                -t['materia'].horas_semanales,
                -len(t['materia'].dias_asignados) if t['materia'].dias_asignados else 0
            ))
            
            if intento > 0:
                random.shuffle(tareas)
            
            total_tareas = len(tareas)
            asignadas = 0
            
            for idx, tarea in enumerate(tareas):
                docente = tarea['docente']
                materia = tarea['materia']
                
                if self.progress_callback and idx % 20 == 0:
                    porcentaje = 10 + int((idx / total_tareas) * 80)
                    self.progress_callback(porcentaje, f"Asignando {materia.nombre} - {docente.nombre}")
                
                asignado = False
                
                # Determinar días a probar
                if materia.dias_asignados:
                    dias_a_probar = [d for d in self.dias if d in materia.dias_asignados]
                else:
                    dias_a_probar = self.dias.copy()
                
                # Eliminar día libre del docente
                if docente.dia_libre and docente.dia_libre != "Ninguno":
                    if docente.dia_libre in dias_a_probar:
                        dias_a_probar.remove(docente.dia_libre)
                
                if intento > 0:
                    random.shuffle(dias_a_probar)
                
                # Probar días y bloques
                for dia in dias_a_probar:
                    bloques_a_probar = self.bloques.copy()
                    if intento > 0:
                        random.shuffle(bloques_a_probar)
                    
                    for bloque in bloques_a_probar:
                        # Verificar disponibilidad
                        if (dia, bloque, docente.cedula) in docente_ocupado:
                            continue
                        if (dia, bloque, materia.id_seccion) in seccion_ocupada:
                            continue
                        
                        # Verificar materia fuerte (máx 2 por día/sección)
                        if materia.nombre in self.MATERIAS_FUERTES:
                            clave_seccion = (dia, materia.id_seccion)
                            if fuertes_por_seccion.get(clave_seccion, 0) >= 2:
                                continue
                            clave_docente = (dia, docente.cedula)
                            if fuertes_por_docente.get(clave_docente, 0) >= 2:
                                continue
                        
                        # Verificar no duplicar materia el mismo día
                        if (dia, materia.id_seccion, materia.nombre) in materia_por_dia:
                            continue
                        
                        # ¡ASIGNAR!
                        self.horario_maestro[(dia, bloque, materia.id_seccion)] = {
                            "materia": materia.nombre,
                            "docente": docente.nombre,
                            "cedula": docente.cedula
                        }
                        
                        docente_ocupado.add((dia, bloque, docente.cedula))
                        seccion_ocupada.add((dia, bloque, materia.id_seccion))
                        materia_por_dia.add((dia, materia.id_seccion, materia.nombre))
                        
                        if materia.nombre in self.MATERIAS_FUERTES:
                            clave_seccion = (dia, materia.id_seccion)
                            fuertes_por_seccion[clave_seccion] = fuertes_por_seccion.get(clave_seccion, 0) + 1
                            clave_docente = (dia, docente.cedula)
                            fuertes_por_docente[clave_docente] = fuertes_por_docente.get(clave_docente, 0) + 1
                        
                        materia.horas_restantes -= 2
                        asignado = True
                        asignadas += 1
                        break
                    
                    if asignado:
                        break
                
                if not asignado:
                    self.materias_no_asignadas.append({
                        "docente": docente.nombre,
                        "materia": materia.nombre,
                        "seccion": materia.id_seccion,
                        "horas": materia.horas_semanales,
                        "dias_restrictivos": materia.dias_asignados,
                        "dia_libre_docente": docente.dia_libre
                    })
            
            porcentaje_asignacion = (asignadas / total_tareas) * 100 if total_tareas > 0 else 0
            
            if porcentaje_asignacion >= 80:
                if self.progress_callback:
                    self.progress_callback(100, f"¡Horario generado! {asignadas}/{total_tareas} bloques")
                return True
        
        if self.progress_callback:
            porcentaje = int((asignadas / total_tareas) * 100) if total_tareas > 0 else 0
            self.progress_callback(100, f"Horario parcial: {asignadas}/{total_tareas} bloques ({porcentaje}%)")
        
        return len(self.horario_maestro) > 0
    
    def generar_y_persistir(self):
        from data_base import guardar_horario_maestro
        
        problemas, advertencias = self.diagnosticar_factibilidad()
        
        if problemas:
            mensaje = "No se puede generar horario:\n"
            for p in problemas:
                mensaje += f"- {p['nombre']}: {p['horas']}h > {p['maximo']}h\n"
            return False, mensaje
        
        exito = self.generar_horario()
        
        if not self.horario_maestro:
            return False, "No se pudo generar el horario."
        
        exito_bd = guardar_horario_maestro(self.horario_maestro)
        if not exito_bd:
            return False, "El horario se generó pero no se pudo guardar."
        
        try:
            exportar_a_pdf(self.horario_maestro, nombre_archivo="horario_liceo.pdf")
            mensaje_extra = " y exportado a PDF"
        except Exception as e:
            print(f"Error exportando PDF: {e}")
            mensaje_extra = ""
        
        if self.materias_no_asignadas:
            return True, f"Horario generado con {len(self.horario_maestro)} asignaciones. {len(self.materias_no_asignadas)} materia(s) no asignadas.{mensaje_extra}"
        
        return True, f"Horario generado exitosamente con {len(self.horario_maestro)} asignaciones.{mensaje_extra}"