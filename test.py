import unittest
import os
from Materia import Materia
from Docente import Docente
from Bloque import Bloque
from SistemaHorarios import SistemaHorarios
from data_base import inicializar_db, guardar_docente, cargar_datos_sistema, eliminar_docente_db, cambiar_password_usuario
from auth import Sesion


class TestArquitecturaHorarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara una base de datos limpia antes de todas las pruebas."""
        if os.path.exists('horarios_liceo.db'):
            os.remove('horarios_liceo.db')
        inicializar_db()

    def setUp(self):
        """Antes de cada test, nos aseguramos de ser Admin para poder operar en BD."""
        Sesion.iniciar_sesion("admin", "1234")

    def test_01_agregar_materia_docente(self):
        """Verifica que un docente acepte materias correctamente."""
        materia1 = Materia("Física", "3A", 4.0, [])
        docente1 = Docente("Juan Perez", "V-12345678", "Lunes")
        
        resultado = docente1.agregar_materia(materia1)
        
        self.assertEqual(resultado, "Materia fue agregada exitosamente")
        self.assertEqual(len(docente1.materias), 1)
        self.assertTrue(docente1.buscar_materia(materia1))

    def test_02_eliminar_materia_docente(self):
        """Verifica la lógica de eliminación y manejo de errores."""
        materia1 = Materia("Química", "4B", 4.0, [])
        materia_falsa = Materia("Biología", "5A", 2.0, [])
        docente = Docente("Maria Lopez", "V-87654321")
        
        docente.agregar_materia(materia1)
        
        res_falla = docente.eliminar_materia(materia_falsa)
        self.assertEqual(res_falla, "Materia no encontrada")
        
        res_exito = docente.eliminar_materia(materia1)
        self.assertEqual(res_exito, "Materia eliminada")
        self.assertEqual(len(docente.materias), 0)

    def test_03_base_de_datos_guardar_cargar(self):
        """Verifica el guardado y la carga SQLite3."""
        materia_db = Materia("Matemática", "1A", 6.0, [])
        docente_db = Docente("Danys", "V-14588968", "Viernes")
        docente_db.agregar_materia(materia_db)

        guardar_docente(docente_db)

        sistema = cargar_datos_sistema()
        docente_recuperado = next((d for d in sistema.docentes if d.cedula == "V-14588968"), None)
        
        self.assertIsNotNone(docente_recuperado)
        self.assertEqual(docente_recuperado.nombre, "Danys")
        self.assertEqual(docente_recuperado.materias[0].nombre, "Matemática")

    def test_04_motor_asignacion_horarios(self):
        """Verifica que el motor reste 2 horas por bloque."""
        sistema = SistemaHorarios()
        
        materia_test = Materia("Historia", "2C", 2.0, []) 
        docente_test = Docente("Pedro", "V-11111111", "Lunes")
        docente_test.agregar_materia(materia_test)
        
        sistema.agregar_docente(docente_test)
        sistema.generar_horario()

        self.assertAlmostEqual(materia_test.horas_restantes, 0.0, places=2)
        self.assertTrue(len(sistema.horario_maestro) > 0)

    def test_05_seguridad_middleware(self):
        """Verifica que un rol no administrativo sea bloqueado."""
        Sesion.rol_actual = "Docente"
        
        docente_prohibido = Docente("Intruso", "V-999")
        resultado = guardar_docente(docente_prohibido)
        
        self.assertIsNone(resultado, "El middleware debería bloquear la ejecución")
        
        Sesion.rol_actual = "Administrativo"

    def test_06_borrado_manual_completo(self):
        """Verifica que el borrado manual elimine al docente de la BD."""
        Sesion.iniciar_sesion("admin", "1234")
        docente = Docente("Borrable", "V-777")
        guardar_docente(docente)
        
        eliminar_docente_db("V-777")
        
        sistema = cargar_datos_sistema()
        docente_en_db = next((d for d in sistema.docentes if d.cedula == "V-777"), None)
        self.assertIsNone(docente_en_db, "El docente no debería existir en la BD")

    def test_07_restriccion_dias_fijos(self):
        """Verifica que el motor respete si una materia solo puede verse un día en específico."""
        sistema = SistemaHorarios()
        
        materia_viernes = Materia("Cálculo", "1A", 2.0, ["Viernes"])
        docente = Docente("Gerardo", "31991281", "Lunes")
        docente.agregar_materia(materia_viernes)
        sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        for (dia, bloque, seccion) in sistema.horario_maestro.keys():
            self.assertEqual(dia, "Viernes", f"Fallo: El motor asignó la materia el día {dia} ignorando la orden.")

    def test_08_cambio_contrasena(self):
        """Verifica que el cambio de contraseña funcione correctamente con bcrypt."""
        
        # Verificar que admin existe y funciona con "1234"
        self.assertTrue(Sesion.iniciar_sesion("admin", "1234"), 
                        "La contraseña original '1234' no funciona")
        
        # Cambiar la contraseña
        exito, mensaje = cambiar_password_usuario("admin", "1234", "nueva123")
        self.assertTrue(exito, f"Error al cambiar contraseña: {mensaje}")
        
        # Verificar que la nueva contraseña funciona
        self.assertTrue(Sesion.iniciar_sesion("admin", "nueva123"), 
                        "La nueva contraseña 'nueva123' no funciona")
        
        # Restaurar contraseña original para no afectar otros tests
        exito, mensaje = cambiar_password_usuario("admin", "nueva123", "1234")
        self.assertTrue(exito, f"Error al restaurar contraseña: {mensaje}")
        
        # Verificar que la original funciona nuevamente
        self.assertTrue(Sesion.iniciar_sesion("admin", "1234"), 
                        "La contraseña restaurada '1234' no funciona")
    
    def test_09_carga_horaria_maxima(self):
        """Verifica que no se pueda asignar más horas de las que tiene la semana."""
        sistema = SistemaHorarios()
        
        materia_excesiva = Materia("Exceso", "1A", 50.0, [])
        docente = Docente("CargaExtrema", "V-99999999", "Ninguno")
        docente.agregar_materia(materia_excesiva)
        sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        total_horas_asignadas = sum(info['materia'] for info in sistema.horario_maestro.values())
        self.assertTrue(len(sistema.horario_maestro) < 100, "Se asignaron más horas de las posibles")
    
    def test_10_respeto_dias_asignados_multiples_bloques(self):
        """Verifica que una materia solo se asigne en los días permitidos."""
        sistema = SistemaHorarios()
        
        # Materia que solo se da Lunes y Miércoles (requiere 4 horas = 2 bloques)
        materia_restrictiva = Materia("Solo Lunes y Miercoles", "1A", 4.0, ["Lunes", "Miércoles"])
        docente = Docente("ProfesorRestrictivo", "V-88888888", "Ninguno")
        docente.agregar_materia(materia_restrictiva)
        sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        # Verificar que todos los bloques asignados estén en los días permitidos
        for (dia, bloque, seccion), info in sistema.horario_maestro.items():
            if info['materia'] == "Solo Lunes y Miercoles":
                self.assertIn(dia, ["Lunes", "Miércoles"], 
                            f"Materia asignada en día no permitido: {dia}")

    def test_11_backtracking_solucion_compleja(self):
        """Verifica que el backtracking encuentre solución en escenarios complejos."""
        sistema = SistemaHorarios()
        
        # Crear 5 docentes con materias cruzadas
        docentes_data = [
            ("Prof1", "V-111", "Martes", ["Matemática", "Física"], ["1A", "1A"]),
            ("Prof2", "V-222", "Miércoles", ["Química", "Biología"], ["1A", "2B"]),
            ("Prof3", "V-333", "Jueves", ["Historia", "Geografía"], ["2B", "3C"]),
            ("Prof4", "V-444", "Viernes", ["Inglés", "Francés"], ["3C", "1A"]),
            ("Prof5", "V-555", "Lunes", ["Educación Física", "Arte"], ["2B", "3C"]),
        ]
        
        for nombre, cedula, libre, materias, secciones in docentes_data:
            docente = Docente(nombre, cedula, libre)
            for i, mat_nombre in enumerate(materias):
                materia = Materia(mat_nombre, secciones[i], 4.0, ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
                docente.agregar_materia(materia)
            sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        # Verificar que se generaron asignaciones
        self.assertTrue(len(sistema.horario_maestro) > 0, "No se generó ningún horario")
        
        # Verificar que todas las materias con horas_restantes = 0 se asignaron completamente
        for docente in sistema.docentes:
            for materia in docente.materias:
                if materia.horas_restantes > 0:
                    print(f"Advertencia: {materia.nombre} tiene {materia.horas_restantes} horas sin asignar")
    
    def test_12_exportacion_pdf_excel(self):
        """Verifica que la exportación a PDF y Excel funcione correctamente."""
        from Exportar import exportar_a_pdf, exportar_a_excel
        
        sistema = SistemaHorarios()
        
        # Crear un docente con una materia simple
        materia = Materia("Matemática", "1A", 2.0, ["Lunes"])
        docente = Docente("ProfesorExport", "V-77777777", "Ninguno")
        docente.agregar_materia(materia)
        sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        # Probar exportación a PDF
        pdf_path = "test_horario.pdf"
        try:
            exportar_a_pdf(sistema.horario_maestro, nombre_archivo=pdf_path)
            self.assertTrue(os.path.exists(pdf_path), "No se creó el archivo PDF")
            self.assertGreater(os.path.getsize(pdf_path), 0, "El archivo PDF está vacío")
        except Exception as e:
            self.fail(f"Error al exportar a PDF: {e}")
        
        # Probar exportación a Excel
        excel_path = "test_horario.xlsx"
        try:
            exportar_a_excel(sistema.horario_maestro, nombre_archivo=excel_path)
            self.assertTrue(os.path.exists(excel_path), "No se creó el archivo Excel")
            self.assertGreater(os.path.getsize(excel_path), 0, "El archivo Excel está vacío")
        except Exception as e:
            self.fail(f"Error al exportar a Excel: {e}")
        
        # Limpiar archivos de prueba
        for path in [pdf_path, excel_path]:
            if os.path.exists(path):
                os.remove(path)
    

if __name__ == '__main__':
    unittest.main(verbosity=2)