import sqlite3
from Docente import Docente
from Materia import Materia
from SistemaHorarios import SistemaHorarios 
from Login import requiere_admin 

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
    
    conn.commit()
    conn.close()

@requiere_admin
def guardar_docente(docente: Docente):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO docentes (cedula, nombre, dia_libre) 
            VALUES (?, ?,?)
        ''', (docente.cedula, docente.nombre,docente.dia_libre))

        cursor.execute('DELETE FROM materias WHERE cedula_docente = ?', (docente.cedula,))

        for m in docente.materias:
            # Convertimos la lista de días a texto separado por comas
            dias_texto = ",".join(m.dias_asignados) if hasattr(m, 'dias_asignados') else ""
            
            cursor.execute('''
                INSERT INTO materias (nombre, id_seccion, horas_semanales, cedula_docente, dias_asignados)
                VALUES (?, ?, ?, ?, ?)
            ''', (m.nombre, m.id_seccion, m.horas_semanales, docente.cedula, dias_texto))
        
        conn.commit()
        print("¡Docente y materias guardados exitosamente!")
    except sqlite3.Error as e:
        print(f"Error al guardar en BD: {e}")
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