```mermaid
classDiagram
    direction TB

    %% Notas arquitectónicas
    note for SistemaHorarios "Motor del sistema\Actualizado a Algoritmo Greedy"

    class SistemaHorarios {
        +Set MATERIAS_FUERTES$
        -List~Docente~ docentes
        -List dias
        -List bloques
        -Dict horario_maestro
        -Callable progress_callback
        -List materias_no_asignadas
        +set_progress_callback(callback: Callable) void
        +agregar_docente(docente: Docente) String
        +diagnosticar_factibilidad() Tuple
        +generar_horario(max_intentos: int) Boolean
        +generar_y_persistir() Tuple
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
    
    Docente "1" o-- "0..*" Materia : dicta
    Seccion "1" *-- "1..*" Materia : cursa
    
    Docente "1" --> "0..1" Horario : tiene asignado
    Seccion "1" --> "0..1" Horario : tiene asignado
    
    Horario "1" *-- "0..*" Bloque : compuesto por
    Bloque "0..*" --> "1" Materia : contiene

```
