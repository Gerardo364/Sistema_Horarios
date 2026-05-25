from Docente import Docente
from Materia import Materia
from data_base import (inicializar_db, cargar_datos_sistema, guardar_docente, 
                       eliminar_docente_db, guardar_usuario_db, cambiar_password_usuario,
                       guardar_materia_catalogo, cargar_materias_catalogo, 
                       eliminar_materia_catalogo, actualizar_materia_catalogo)
from auth import Sesion
from Exportar import exportar_a_pdf
import bcrypt

def menu():
    print("--- INICIO DE SESIÓN LICEO ---")
    usuario = input("Ingrese su nombre de usuario: ").strip()
    password = input("Ingrese su contraseña: ").strip()
    
    if not Sesion.iniciar_sesion(usuario, password): 
        print("\n Usuario o contraseña incorrectos.")
        return 

    print(f"\n Bienvenido, {Sesion.usuario_actual}  (Rol: {Sesion.rol_actual})")
    

    sistema = cargar_datos_sistema()
    
    while True:
        print("\n--- GESTIÓN DE HORARIOS LICEO ---")
        print("1. Registrar Docente")
        print("2. Ver Docentes y Materias")
        print("3. Borrar Docente")
        print("4. Generar Horario y PDF")
        print("5. Cambiar mi contraseña")
        print("6. Gestionar Catálogo de Materias")
        print("7. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            if Sesion.rol_actual != "Administrativo":
                print("\n ACCESO DENEGADO: Solo el personal Administrativo puede registrar docentes.")
                continue
            
            nombre = input("Nombre del docente: ").strip()
            cedula = input("Cédula: ").strip()
            print("Días: Lunes, Martes, Miercoles, Jueves, Viernes")
            libre = input("Día libre: ").capitalize().strip()
            
            nuevo = Docente(nombre, cedula, libre)
            
            print(f"\n--- Creación de cuenta para {nombre} ---")
            user_login = input("Defina nombre de usuario para el login: ").strip()
            pass_login = input("Defina contraseña inicial: ").strip()
            
            guardar_usuario_db(user_login, pass_login, "Docente")
            
            while True:
                print("\n--- Asignar Materias (desde el catálogo) ---")
                # Mostrar catálogo disponible
                catalogo = cargar_materias_catalogo()
                if catalogo:
                    print("Materias disponibles en el catálogo:")
                    for idx, (mid, nombre_mat) in enumerate(catalogo, 1):
                        print(f"  {idx}. {nombre_mat}")
                    print("  0. Crear nueva materia (no está en el catálogo)")
                else:
                    print("No hay materias en el catálogo. Debes crear una nueva.")
                
                seleccion = input("\nSeleccione una materia por su número (o 'fin' para terminar): ").strip()
                if seleccion.lower() == 'fin':
                    break
                
                try:
                    seleccion_int = int(seleccion)
                    if seleccion_int == 0:
                        # Crear nueva materia
                        nom_materia = input("Nombre de la nueva materia: ").strip()
                        if guardar_materia_catalogo(nom_materia):
                            print(f" Materia '{nom_materia}' añadida al catálogo.")
                        else:
                            print(" Error: No se pudo guardar la materia.")
                            continue
                    elif 1 <= seleccion_int <= len(catalogo):
                        nom_materia = catalogo[seleccion_int - 1][1]
                    else:
                        print(" Opción no válida.")
                        continue
                except ValueError:
                    print(" Opción no válida.")
                    continue
    
                seccion = input(f"Sección para {nom_materia}: ").upper().strip()
                horas = float(input(f"Horas semanales para {nom_materia}: "))
                
                print("Ejemplo: Lunes,Miércoles (Deje en blanco para cualquier día)")
                dias_input = input(f"Días asignados para {nom_materia} en {seccion}: ").strip()
                
                if dias_input:
                    lista_dias = [d.strip().capitalize() for d in dias_input.split(",")]
                else:
                    lista_dias = []

                nueva_materia = Materia(nom_materia, seccion, horas, lista_dias)
                nuevo.agregar_materia(nueva_materia)
                print(f" {nom_materia} agregada para los días: {lista_dias if lista_dias else 'Libre'}")
            guardar_docente(nuevo)
            sistema = cargar_datos_sistema()
            print(f"\n Docente {nombre} registrado correctamente.")  
        elif opcion == "2":
            sistema = cargar_datos_sistema() 
            if not sistema.docentes:
                print("\n No hay docentes registrados.")
            for d in sistema.docentes:
                print(f"\nDocente: {d.nombre} ({d.cedula}) | Día Libre: {d.dia_libre}")
                for m in d.materias:
                    dias_info = f" | Días: {m.dias_asignados}" if m.dias_asignados else " | Días: Libre"
                    print(f"  - {m.nombre} | Sección: {m.id_seccion} | {m.horas_semanales}h{dias_info}")
        
        elif opcion == "3":
            if Sesion.rol_actual != "Administrativo":
                print("\n ACCESO DENEGADO: No tiene permisos para borrar registros.")
                continue
            
            cedula_a_borrar = input("Ingrese la cédula del docente a eliminar: ").strip()
            confirmar = input(f"¿Está seguro de eliminar al docente con cédula {cedula_a_borrar}? (s/n): ").lower()
            if confirmar == 's':
                eliminar_docente_db(cedula_a_borrar)
                sistema = cargar_datos_sistema()
                print(" Docente eliminado.")
            else:
                print(" Operación cancelada.")
        
        elif opcion == "4":
            if Sesion.rol_actual == "Administrativo":
                print("\n Generando horario óptimo...")
                sistema = cargar_datos_sistema()
                exito, mensaje = sistema.generar_y_persistir()
                
                if exito:
                    print(f" ¡{mensaje}!")
                else:
                    print(f" Error: {mensaje}")
            else:
                print("No tiene permisos para generar horarios.")
         
        elif opcion == "5":
            print("\n--- Cambiar Contraseña ---")
            actual = input("Contraseña actual: ").strip()
            nueva = input("Nueva contraseña: ").strip()
            confirm = input("Confirmar nueva contraseña: ").strip()

            if nueva != confirm:
                print(" Las contraseñas nuevas no coinciden.")
            elif not actual or not nueva:
                print(" Complete todos los campos.")
            else:
                exito, mensaje = cambiar_password_usuario(Sesion.usuario_actual, actual, nueva)
                if exito:
                    print(f" {mensaje}")
                else:
                    print(f" Error: {mensaje}")
                                          
        elif opcion == "6":

                if Sesion.rol_actual != "Administrativo":
                    print("\n ACCESO DENEGADO: Solo el personal Administrativo puede gestionar materias.")
                    continue
                
                while True:
                    print("\n--- CATÁLOGO DE MATERIAS ---")
                    print("1. Ver todas las materias")
                    print("2. Agregar nueva materia")
                    print("3. Editar materia existente")
                    print("4. Eliminar materia")
                    print("5. Volver al menú principal")
                    
                    sub_opcion = input("Seleccione una opción: ").strip()
                    
                    if sub_opcion == "1":
                        catalogo = cargar_materias_catalogo()
                        if not catalogo:
                            print("\n No hay materias en el catálogo.")
                        else:
                            print("\n Materias disponibles:")
                            for idx, (mid, nombre) in enumerate(catalogo, 1):
                                print(f"  {idx}. ID: {mid} | {nombre}")
                    
                    elif sub_opcion == "2":
                        nombre = input("Nombre de la nueva materia: ").strip()
                        if not nombre:
                            print(" Nombre no válido.")
                            continue
                        if guardar_materia_catalogo(nombre):
                            print(f" Materia '{nombre}' añadida al catálogo.")
                        else:
                            print(" Error: La materia ya existe o hubo un problema.")
                    
                    elif sub_opcion == "3":
                        catalogo = cargar_materias_catalogo()
                        if not catalogo:
                            print(" No hay materias para editar.")
                            continue
                        print("\n Materias disponibles:")
                        for idx, (mid, nombre) in enumerate(catalogo, 1):
                            print(f"  {idx}. {nombre}")
                        try:
                            seleccion = int(input("Seleccione el número de la materia a editar: ").strip())
                            if 1 <= seleccion <= len(catalogo):
                                materia_id, nombre_actual = catalogo[seleccion - 1]
                                nuevo_nombre = input(f"Nuevo nombre (actual: {nombre_actual}): ").strip()
                                if nuevo_nombre:
                                    exito, mensaje = actualizar_materia_catalogo(materia_id, nuevo_nombre)
                                    if exito:
                                        print(f" {mensaje}")
                                    else:
                                        print(f" Error: {mensaje}")
                                else:
                                    print(" Nombre no válido.")
                            else:
                                print(" Opción no válida.")
                        except ValueError:
                            print(" Entrada no válida.")
                    
                    elif sub_opcion == "4":
                        catalogo = cargar_materias_catalogo()
                        if not catalogo:
                            print(" No hay materias para eliminar.")
                            continue
                        print("\n Materias disponibles:")
                        for idx, (mid, nombre) in enumerate(catalogo, 1):
                            print(f"  {idx}. {nombre}")
                        try:
                            seleccion = int(input("Seleccione el número de la materia a eliminar: ").strip())
                            if 1 <= seleccion <= len(catalogo):
                                materia_id, nombre = catalogo[seleccion - 1]
                                confirmar = input(f"¿Eliminar la materia '{nombre}'? (s/n): ").lower()
                                if confirmar == 's':
                                    eliminar_materia_catalogo(materia_id)
                                    print(f" Materia '{nombre}' eliminada.")
                                else:
                                    print(" Operación cancelada.")
                            else:
                                print(" Opción no válida.")
                        except ValueError:
                            print(" Entrada no válida.")
                    
                    elif sub_opcion == "5":
                        break
                    
                    else:
                        print(" Opción no válida.")
        elif opcion == "7":
            print("\n ¡Hasta luego!")
            break

        else:
            print(" Opción no válida.")


if __name__ == "__main__":
    inicializar_db()
    menu()