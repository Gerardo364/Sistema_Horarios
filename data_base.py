import sqlite3
from Docente import Docente
from Materia import Materia
from SistemaHorarios import SistemaHorarios 
from auth import requiere_admin
import bcrypt


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


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
            dia_libre TEXT,
            usuario TEXT
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
        nombre TEXT UNIQUE
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
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        accion TEXT,
        detalle TEXT,
        usuario TEXT
    )
    ''')
    # Migrar contraseña de admin a hash si está en texto plano
    cursor.execute("SELECT password FROM usuarios WHERE usuario = 'admin'")
    admin_pass = cursor.fetchone()
    if admin_pass and not admin_pass[0].startswith('$2b$'):  # no es hash bcrypt
        hashed_admin = _hash_password(admin_pass[0])
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = 'admin'", (hashed_admin,))
        conn.commit()
        print("Contraseña de admin migrada a hash.")
        
    conn.commit()
    conn.close()


def registrar_log(accion, detalle):
    from auth import Sesion
    usuario = Sesion.usuario_actual if Sesion.usuario_actual else "sistema"
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (accion, detalle, usuario) VALUES (?, ?, ?)",
                   (accion, detalle, usuario))
    conn.commit()
    conn.close()
    

def obtener_ultimos_logs(limite=5):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fecha, accion, detalle, usuario FROM logs
        ORDER BY fecha DESC LIMIT ?
    ''', (limite,))
    logs = cursor.fetchall()
    conn.close()
    return logs


def obtener_alertas():
    alertas = []
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    # Docentes sin materias
    cursor.execute('''
        SELECT COUNT(*) FROM docentes d
        LEFT JOIN materias m ON d.cedula = m.cedula_docente
        WHERE m.id IS NULL
    ''')
    sin_materias = cursor.fetchone()[0]
    if sin_materias > 0:
        alertas.append(f"{sin_materias} docente(s) sin materias asignadas.")
    cursor.execute("SELECT COUNT(DISTINCT id_seccion) FROM materias")
    total_secciones = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT id_seccion) FROM horarios_generados")
    secciones_con_horario = cursor.fetchone()[0]
    sin_horario = total_secciones - secciones_con_horario
    if sin_horario > 0:
        alertas.append(f"{sin_horario} sección(es) sin horario generado.")
    conn.close()
    return alertas


@requiere_admin
def guardar_docente(docente: Docente):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO docentes (cedula, nombre, dia_libre,usuario) 
            VALUES (?, ?, ?, ?)
        ''', (docente.cedula, docente.nombre, docente.dia_libre, docente.usuario))

        cursor.execute('DELETE FROM materias WHERE cedula_docente = ?', (docente.cedula,))

        for m in docente.materias:
            dias_texto = ",".join(m.dias_asignados) if hasattr(m, 'dias_asignados') else ""
            cursor.execute('''
                INSERT INTO materias (nombre, id_seccion, horas_semanales, cedula_docente, dias_asignados)
                VALUES (?, ?, ?, ?, ?)
            ''', (m.nombre, m.id_seccion, m.horas_semanales, docente.cedula, dias_texto))

        conn.commit()
        registrar_log("REGISTRO_DOCENTE", f"Docente {docente.nombre} ({docente.cedula})")
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
        cursor.execute("SELECT usuario FROM docentes WHERE cedula = ?", (cedula,))
        row = cursor.fetchone()
        usuario = row[0] if row else None
        cursor.execute('DELETE FROM materias WHERE cedula_docente = ?', (cedula,))
        cursor.execute('DELETE FROM docentes WHERE cedula = ?', (cedula,))
        
        if usuario:
            cursor.execute('DELETE FROM usuarios WHERE usuario = ?', (usuario,))
        
        conn.commit()
        if cursor.rowcount > 0:
            registrar_log("ELIMINACION_DOCENTE", f"Docente cédula {cedula} eliminado")
            print(f"Éxito: Registro con cédula {cedula} y sus materias eliminados.")
        else:
            print("No se encontró ningún docente con esa cédula.")
    except sqlite3.Error as e:
        print(f"Error al eliminar en BD: {e}")
    finally:
        conn.close()

def cargar_docente_por_cedula(cedula):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cedula, nombre, dia_libre, usuario FROM docentes WHERE cedula = ?', (cedula,))
    row = cursor.fetchone()
    conn.close()
    if row:
        docente = Docente(row[1], row[0], row[2])
        docente.usuario = row[3]
        # Cargar sus materias
        conn2 = sqlite3.connect('horarios_liceo.db')
        cursor2 = conn2.cursor()
        cursor2.execute('SELECT nombre, id_seccion, horas_semanales, dias_asignados FROM materias WHERE cedula_docente = ?', (cedula,))
        for m_nombre, m_seccion, m_horas, m_dias in cursor2.fetchall():
            lista_dias = m_dias.split(",") if m_dias else []
            materia = Materia(m_nombre, m_seccion, m_horas, lista_dias)
            docente.agregar_materia(materia)
        conn2.close()
        return docente
    return None

def cargar_datos_sistema():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    sistema = SistemaHorarios()

    try:
        cursor.execute('SELECT cedula, nombre, dia_libre, usuario FROM docentes')
        filas_docentes = cursor.fetchall()

        for cedula, nombre, dia_libre, usuario in filas_docentes: 
            nuevo_docente = Docente(nombre, cedula, dia_libre, usuario=usuario) 
            
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

def guardar_materia_catalogo(nombre):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO catalogo_materias (nombre) VALUES (?)', (nombre,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"La materia '{nombre}' ya existe.")
        return False
    except sqlite3.Error as e:
        print(f"Error guardando materia: {e}")
        return False
    finally:
        conn.close()

def cargar_materias_catalogo():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre FROM catalogo_materias ORDER BY nombre')
    materias = cursor.fetchall()
    conn.close()
    return materias  # lista de (id, nombre)

# Opcional: eliminar materia del catálogo
def eliminar_materia_catalogo(materia_id):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM catalogo_materias WHERE id = ?', (materia_id,))
    conn.commit()
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
        registrar_log("GENERACION_HORARIO", f"Horario generado con {len(horario_maestro)} asignaciones")
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar horario: {e}")
        return False
    finally:
        conn.close()
   
        
def obtener_usuarios():
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, rol FROM usuarios ORDER BY usuario")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def guardar_usuario_db(usuario, password, rol):
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        hashed = _hash_password(password)
        cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", 
                       (usuario, hashed, rol))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: El usuario '{usuario}' ya existe.")
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


def cambiar_password_usuario(usuario, password_actual, password_nueva):
    # Limpiar espacios
    usuario = usuario.strip()
    password_actual = password_actual.strip()
    password_nueva = password_nueva.strip()

    if not usuario or not password_actual or not password_nueva:
        return False, "Todos los campos son obligatorios."

    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT password FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return False, "Usuario no encontrado."
        
        if not _check_password(password_actual, resultado[0]):
            return False, "La contraseña actual es incorrecta."
        
        nuevo_hash = _hash_password(password_nueva)
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = ?", (nuevo_hash, usuario))
        
        if cursor.rowcount == 0:
            return False, "No se pudo actualizar la contraseña."
        
        conn.commit()
        return True, "Contraseña cambiada correctamente."
    
    except sqlite3.Error as e:
        return False, f"Error de base de datos: {e}"
    finally:
        conn.close()
        
def actualizar_password_directa(usuario, nueva_password):
    """Actualiza la contraseña de un usuario directamente (para uso del Admin al editar)."""
    conn = sqlite3.connect('horarios_liceo.db')
    cursor = conn.cursor()
    try:
        hashed = _hash_password(nueva_password)
        cursor.execute("UPDATE usuarios SET password = ? WHERE usuario = ?", (hashed, usuario))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al forzar actualización de contraseña: {e}")
        return False
    finally:
        conn.close()