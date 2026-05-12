from Docente import Docente
from Materia import Materia
from data_base import inicializar_db, cargar_datos_sistema, guardar_docente, eliminar_docente_db, guardar_horario_maestro,guardar_usuario_db
from Login import Sesion
from Exportar import exportar_a_pdf

def menu():
    print("--- INICIO DE SESIÓN LICEO ---")
    usuario = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    
    if not Sesion.iniciar_sesion(usuario, password): 
        print("\n Usuario o contraseña incorrectos.")
        return 

    print(f"\n Bienvenido, {Sesion.usuario_actual}")
    

    sistema = cargar_datos_sistema()
    
    while True:
        print("\n--- GESTIÓN DE HORARIOS LICEO ---")
        print("1. Registrar Docente")
        print("2. Ver Docentes y Materias")
        print("3. Borrar Docente")
        print("4. Generar Horario y PDF")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            if Sesion.rol_actual != "Administrativo":
                print("\n ACCESO DENEGADO: Solo el personal Administrativo puede registrar docentes.")
                continue
            
            nombre = input("Nombre del docente: ")
            cedula = input("Cédula: ")
            print("Días: Lunes, Martes, Miercoles, Jueves, Viernes")
            libre = input("Día libre: ").capitalize()
            
            nuevo = Docente(nombre, cedula, libre)
            
            print(f"\n--- Creación de cuenta para {nombre} ---")
            user_login = input("Defina nombre de usuario para el login: ")
            pass_login = input("Defina contraseña inicial: ")
            
            guardar_usuario_db(user_login, pass_login, "Docente")
            
            while True:
                nom_materia = input("\nNombre de la materia (o escribe 'fin' para terminar): ")
                if nom_materia.lower() == 'fin':
                    break
                    
                seccion = input(f"Sección para {nom_materia}: ").upper()
                horas = float(input(f"Horas semanales para {nom_materia}: "))

                print("Ejemplo: Lunes,Miercoles (Deje en blanco para cualquier día)")
                dias_input = input(f"Días asignados para {nom_materia} en {seccion}: ")
                
                if dias_input.strip():
                    lista_dias = [d.strip().capitalize() for d in dias_input.split(",")]
                else:
                    lista_dias = []

                nueva_materia = Materia(nom_materia, seccion, horas, lista_dias)
                nuevo.agregar_materia(nueva_materia)
                print(f" {nom_materia} agregada para los días: {lista_dias if lista_dias else 'Libre'}") 
            
            guardar_docente(nuevo)
            sistema = cargar_datos_sistema()
                
        elif opcion == "2":
            sistema = cargar_datos_sistema() 
            for d in sistema.docentes:
                print(f"\nDocente: {d.nombre} ({d.cedula}) | Día Libre: {d.dia_libre}")
                for m in d.materias:
                    dias_info = f" | Días: {m.dias_asignados}" if m.dias_asignados else " | Días: Libre"
                    print(f"  - {m.nombre} | Sección: {m.id_seccion} | {m.horas_semanales}h{dias_info}")
        
        elif opcion == "3":
            if Sesion.rol_actual != "Administrativo":
                print("\n ACCESO DENEGADO: No tiene permisos para borrar registros.")
                continue
            
            cedula_a_borrar = input("Ingrese la cédula del docente a eliminar: ")
            eliminar_docente_db(cedula_a_borrar)
            sistema = cargar_datos_sistema()
        
        elif opcion == "4":
            if Sesion.rol_actual == "Administrativo":
                print("\n Generando horario óptimo...")
                sistema = cargar_datos_sistema()
                sistema.generar_horario()
                
                if sistema.horario_maestro:
                    guardar_horario_maestro(sistema.horario_maestro)
                    exportar_a_pdf(sistema.horario_maestro)
                    print("¡Horario generado y exportado a PDF!")
                else:
                    print(" No se pudo generar el horario. Verifique que las horas y días coincidan.")
            else:
                print("No tiene permisos para generar horarios.")
                               
        elif opcion == "5":
            break

if __name__ == "__main__":
    inicializar_db()
    menu()