```mermaid
classDiagram
    direction TB

    %% Notas arquitectónicas
    note for SistemaHorarios "Motor del sistema\nContiene el algoritmo de Backtracking"

    class SistemaHorarios {
        -List~Docente~ docentes
        -Tuple dias
        -Tuple bloques
        -Dict horario_maestro
        -List~Bloque~ lista_objetos_bloques
        +agregar_docente(docente: Docente) String
        +inicializar_bloques_del_liceo() void
        +generar_horario() void
        +generar_y_persistir() Tuple
        -_asignar_backtrack(tareas, indice) Boolean
        -_es_valido(dia, bloque, docente, materia) Boolean
        -_registrar_estado(dia, bloque, docente, materia, colocar) void
    }

    class Docente {
        -String nombre
        -String cedula
        -String dia_libre
        -String usuario
        -List~Materia~ materias
        -Horario horario
        +asignar_horario(horario: Horario) String
        +agregar_materia(materia: Materia) String
        +eliminar_materia(materia: Materia) String
        +buscar_materia(materia: Materia) Boolean
    }

    class Materia {
        -String nombre
        -String id_seccion
        -float horas_semanales
        -float horas_restantes
        -List dias_asignados
        -List~Bloque~ bloques
    }

    class Seccion {
        -int grado
        -String letra
        -String id_seccion
        -List~Materia~ materias
        -Horario horario
        +asignar_horario(horario: Horario) String
        +__str__() String
    }

    class Horario {
        -String ID
        -List~Bloque~ bloques
        +mostrar() void
    }

    class Bloque {
        -String dia
        -String hora_inicio
        -String hora_final
        -Materia materia
        +obtener_bloque() String
    }

    %% Relaciones con multiplicidad y semántica estricta
    SistemaHorarios "1" *-- "0..*" Docente : gestiona
    SistemaHorarios "1" *-- "0..*" Bloque : inicializa
    
    Docente "1" o-- "0..*" Materia : dicta
    Seccion "1" *-- "1..*" Materia : cursa
    
    Docente "1" --> "0..1" Horario : tiene asignado
    Seccion "1" --> "0..1" Horario : tiene asignado
    
    Horario "1" *-- "0..*" Bloque : compuesto por
    Bloque "0..*" --> "1" Materia : contiene
```
