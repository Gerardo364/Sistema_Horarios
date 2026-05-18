import sqlite3
from Docente import Docente
from Materia import Materia
from SistemaHorarios import SistemaHorarios 
from auth import requiere_admin

def inicializar_db():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            password TEXT,
            rol TEXT
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios VALUES ('admin', '1234', 'Administrativo')")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS docentes (
            cedula TEXT PRIMARY KEY,
            nombre TEXT,
            dia_libre TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            id_seccion TEXT,
            horas_semanales REAL,
            cedula_docente TEXT,
            dias_asignados TEXT,
            FOREIGN KEY (cedula_docente) REFERENCES docentes (cedula)
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catalogo_materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        grado TEXT,
        seccion TEXT,
        horas_semanales REAL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios_generados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT,
        bloque TEXT,
        cedula_docente TEXT,
        id_seccion TEXT,
        materia_nombre TEXT,
        FOREIGN KEY (cedula_docente) REFERENCES docentes (cedula)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

@requiere_admin
def guardar_docente(docente: Docente):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO docentes (cedula, nombre, dia_libre) 
            VALUES (?, ?, ?)
        ''', (docente.cedula, docente.nombre, docente.dia_libre))

        cursor.execute('DELETE FROM materias WHERE cedula_docente = ?', (docente.cedula,))

        for m in docente.materias:
            dias_texto = ",".join(m.dias_asignados) if hasattr(m, 'dias_asignados') else ""
            cursor.execute('''
                INSERT INTO materias (nombre, id_seccion, horas_semanales, cedula_docente, dias_asignados)
                VALUES (?, ?, ?, ?, ?)
            ''', (m.nombre, m.id_seccion, m.horas_semanales, docente.cedula, dias_texto))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar en BD: {e}")
        return False
    finally:
        conn.close()
def existe_docente(cedula):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM docentes WHERE cedula = ?', (cedula,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

@requiere_admin
def eliminar_docente_db(cedula: str):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM materias WHERE cedula_docente = ?', (cedula,))
        cursor.execute('DELETE FROM docentes WHERE cedula = ?', (cedula,))
        
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Éxito: Registro con cédula {cedula} y sus materias eliminados.")
        else:
            print("No se encontró ningún docente con esa cédula.")
    except sqlite3.Error as e:
        print(f"Error al eliminar en BD: {e}")
    finally:
        conn.close()


def cargar_datos_sistema():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    sistema = SistemaHorarios()

    try:
        cursor.execute('SELECT cedula, nombre, dia_libre FROM docentes')
        filas_docentes = cursor.fetchall()

        for cedula, nombre, dia_libre in filas_docentes: 
            nuevo_docente = Docente(nombre, cedula, dia_libre) 
            
            # Cargamos también la columna dias_asignados
            cursor.execute('SELECT nombre, id_seccion, horas_semanales, dias_asignados FROM materias WHERE cedula_docente = ?', (cedula,))
            filas_materias = cursor.fetchall()
            
            for m_nombre, m_seccion, m_horas, m_dias in filas_materias:
                # Convertimos el texto de vuelta a una lista
                lista_dias = m_dias.split(",") if m_dias else []
                # Pasamos la lista al constructor (requiere que modifiques Materia.py)
                nueva_materia = Materia(m_nombre, m_seccion, m_horas, lista_dias)
                nuevo_docente.agregar_materia(nueva_materia)
            
            sistema.agregar_docente(nuevo_docente)
    except sqlite3.Error as e:
        print(f"Error al cargar datos: {e}")
    finally:
        conn.close()
        
    return sistema

def guardar_materia_catalogo(nombre, grado, seccion, horas):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO catalogo_materias (nombre, grado, seccion, horas_semanales)
            VALUES (?, ?, ?, ?)
        ''', (nombre, grado, seccion, horas))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error guardando materia: {e}")
        return False
    finally:
        conn.close()

def cargar_materias_catalogo():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, grado, seccion, horas_semanales FROM catalogo_materias')
    materias = cursor.fetchall()
    conn.close()
    return materias


@requiere_admin
def guardar_horario_maestro(horario_maestro):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM horarios_generados')
        
        for (dia, bloque, id_seccion), info in horario_maestro.items():
            cursor.execute('''
                INSERT INTO horarios_generados (dia, bloque, cedula_docente, id_seccion, materia_nombre)
                VALUES (?, ?, ?, ?, ?)
            ''', (dia, bloque, info['cedula'], id_seccion, info['materia']))
        
        conn.commit()
        print(" Horario guardado en la base de datos exitosamente.")
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar horario: {e}")
        return False
    finally:
        conn.close()

def guardar_usuario_db(usuario, password, rol):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", 
                       (usuario, password, rol))
        conn.commit()
        print(f"Usuario '{usuario}' registrado correctamente.")
    except sqlite3.IntegrityError:
        print(f"Error: El nombre de usuario '{usuario}' ya existe.")
    finally:
        conn.close()

def cargar_horario_maestro():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    horario = {}
    try:
        cursor.execute('SELECT dia, bloque, cedula_docente, id_seccion, materia_nombre FROM horarios_generados')
        for dia, bloque, cedula, seccion, materia in cursor.fetchall():
            # Obtener nombre del docente
            cursor2 = conn.cursor()
            cursor2.execute('SELECT nombre FROM docentes WHERE cedula = ?', (cedula,))
            nombre_docente = cursor2.fetchone()
            cursor2.close()
            horario[(dia, bloque, seccion)] = {
                'materia': materia,
                'cedula': cedula,
                'docente': nombre_docente[0] if nombre_docente else "Desconocido"
            }
    except sqlite3.Error as e:
        print(f"Error cargando horario: {e}")
    finally:
        conn.close()
    return horario

def obtener_nombre_docente(cedula):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM docentes WHERE cedula = ?', (cedula,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "Desconocido"

def obtener_configuracion(clave):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def guardar_configuracion(clave, valor):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, valor))
    conn.commit()
    conn.close()