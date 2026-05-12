import unittest
import os
from Materia import Materia
from Docente import Docente
from Bloque import Bloque
from SistemaHorarios import SistemaHorarios
from data_base import inicializar_db, guardar_docente, cargar_datos_sistema, eliminar_docente_db
from Login import Sesion 

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
        """Verifica que un docente acepte materias correctamente (Docente.py / Materia.py)."""
        # CORRECCIÓN 2: Se añade la lista vacía [] para los días asignados
        materia1 = Materia("Física", "3A", 4.0, [])
        docente1 = Docente("Juan Perez", "V-12345678", "Lunes")
        
        resultado = docente1.agregar_materia(materia1)
        
        self.assertEqual(resultado, "Materia fue agregada exitosamente")
        self.assertEqual(len(docente1.materias), 1)
        self.assertTrue(docente1.buscar_materia(materia1))

    def test_02_eliminar_materia_docente(self):
        """Verifica la lógica de eliminación y manejo de errores (Docente.py)."""
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
        """Verifica el guardado y la carga SQLite3 (data_base.py)."""
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
        
        # CORRECCIÓN 3: Ajustado a 2.0 porque ahora el motor resta 2 fijas
        materia_test = Materia("Historia", "2C", 2.0, []) 
        docente_test = Docente("Pedro", "V-11111111", "Lunes")
        docente_test.agregar_materia(materia_test)
        
        sistema.agregar_docente(docente_test)
        sistema.generar_horario()

        self.assertAlmostEqual(materia_test.horas_restantes, 0.0, places=2)
        self.assertTrue(len(sistema.horario_maestro) > 0)

    def test_05_seguridad_middleware(self):
        """Verifica que un rol no administrativo sea bloqueado."""
        # CORRECCIÓN 4: Forzamos el rol para la prueba en lugar de buscar un usuario inexistente
        Sesion.rol_actual = "Docente"
        
        docente_prohibido = Docente("Intruso", "V-999")
        resultado = guardar_docente(docente_prohibido)
        
        self.assertIsNone(resultado, "El middleware debería bloquear la ejecución")
        
        # Restauramos el rol para no afectar los siguientes tests
        Sesion.rol_actual = "Administrativo"

    def test_06_borrado_manual_completo(self):
        """Verifica que el borrado manual elimine al docente de la BD."""
        # Aseguramos el login por si el test anterior movió el rol
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
        
        # Asignamos que Cálculo solo se pueda dar los Viernes
        materia_viernes = Materia("Cálculo", "1A", 2.0, ["Viernes"])
        docente = Docente("Gerardo", "31991281", "Lunes")
        docente.agregar_materia(materia_viernes)
        sistema.agregar_docente(docente)
        
        sistema.generar_horario()
        
        for (dia, bloque, seccion) in sistema.horario_maestro.keys():
            self.assertEqual(dia, "Viernes", f"Fallo: El motor asignó la materia el día {dia} ignorando la orden.")

if __name__ == '__main__':
    unittest.main(verbosity=2)