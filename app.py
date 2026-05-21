import customtkinter as ctk
import traceback
from tkinter import messagebox
from PIL import Image
from auth import Sesion, requiere_admin
from configuracion import ConfiguracionVista
from Docente import Docente
from Materia import Materia
from data_base import guardar_docente,cargar_datos_sistema,guardar_horario_maestro,cargar_horario_maestro,existe_docente,guardar_materia_catalogo,guardar_usuario_db,cargar_materias_catalogo,obtener_ultimos_logs
from Exportar import exportar_a_pdf


# --- CONFIGURACIÓN DE COLORES ---
COLOR_BG = "#faf9fd"
COLOR_SIDEBAR = "#efedf1"
COLOR_PRIMARY = "#002046"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e3e2e6"
COLOR_TEXT_VARIANT = "#44474e"

# ================================================================
# NUEVA CLASE: VENTANA DE REGISTRO (El código convertido de HTML)
# ================================================================
# ================================================================
# CLASE CORREGIDA: VENTANA DE REGISTRO DE DOCENTE
# ================================================================
class RegistroDocenteVentana(ctk.CTkToplevel):
    def __init__(self, parent, vista_docentes=None):   # <--- nuevo parámetro
        super().__init__(parent)
        self.vista_docentes = vista_docentes
        self.title("Registrar Nuevo Docente")
        self.geometry("750x650")
        self.configure(fg_color=COLOR_BG)
        self.transient(parent)
        self.grab_set()

        # --- Contenedor con scroll ---
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_scroll.pack(fill="both", expand=True, pady=(0, 80))

        # --- Header ---
        header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="Registrar Nuevo Docente",
                     font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header_frame,
                     text="Complete los datos básicos, credenciales de acceso y asigne su carga académica.",
                     font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_VARIANT).pack(anchor="w")

        # --- Formulario básico ---
        info_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        info_frame.pack(fill="x", padx=40, pady=10)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        # Nombre
        ctk.CTkLabel(info_frame, text="Nombre Completo", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 15), pady=(0,5))
        self.entry_nombre = ctk.CTkEntry(info_frame, placeholder_text="Ej. Ana Mendoza", height=40,
                                         border_color=COLOR_BORDER, fg_color=COLOR_CARD)
        self.entry_nombre.grid(row=1, column=0, sticky="ew", padx=(0, 15), pady=(0, 20))

        # Cédula
        ctk.CTkLabel(info_frame, text="Número de Cédula", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w", padx=(15, 0),  pady=(0,5))
        self.entry_cedula = ctk.CTkEntry(info_frame, placeholder_text="V-00.000.000", height=40,
                                         border_color=COLOR_BORDER, fg_color=COLOR_CARD)
        self.entry_cedula.grid(row=1, column=1, sticky="ew", padx=(15, 0), pady=(0, 20))

        # Día Libre
        ctk.CTkLabel(info_frame, text="Día Libre", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=(0, 15), pady=(0,5))
        self.combo_dia = ctk.CTkComboBox(info_frame,
                                         values=["Ninguno","Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
                                         height=40, border_color=COLOR_BORDER, fg_color=COLOR_CARD)
        self.combo_dia.grid(row=3, column=0, sticky="ew", padx=(0, 15), pady=(0, 20))

        # Rol (solo informativo, no se guarda en Docente)
        ctk.CTkLabel(info_frame, text="Rol del Sistema", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, sticky="w", padx=(15, 0),  pady=(0,5))
        self.rol_var = ctk.StringVar(value="Docente")
        rol_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        rol_frame.grid(row=3, column=1, sticky="ew", padx=(15, 0), pady=(0, 20))
        ctk.CTkRadioButton(rol_frame, text="Docente", variable=self.rol_var, value="Docente",
                           text_color=COLOR_TEXT_VARIANT, fg_color=COLOR_PRIMARY).pack(side="left", padx=(0,20))
        ctk.CTkRadioButton(rol_frame, text="Administrativo", variable=self.rol_var, value="Administrativo",
                           text_color=COLOR_TEXT_VARIANT, fg_color=COLOR_PRIMARY).pack(side="left")
    
        # --- Credenciales de Acceso ---
        credenciales_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        credenciales_frame.pack(fill="x", padx=40, pady=(20,10))
        ctk.CTkLabel(credenciales_frame, text="Credenciales de Acceso", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", pady=(0,10))
        ctk.CTkFrame(credenciales_frame, height=2, fg_color=COLOR_BORDER).pack(fill="x", pady=(0,15))

        cred_grid = ctk.CTkFrame(credenciales_frame, fg_color="transparent")
        cred_grid.pack(fill="x")
        cred_grid.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(cred_grid, text="Usuario", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0,15), pady=(0,5))
        self.entry_usuario = ctk.CTkEntry(cred_grid, placeholder_text="Ej. ana.mendoza", height=40,
                                          border_color=COLOR_BORDER, fg_color=COLOR_CARD)
        self.entry_usuario.grid(row=1, column=0, sticky="ew", padx=(0,15), pady=(0,20))

        ctk.CTkLabel(cred_grid, text="Contraseña", text_color=COLOR_TEXT_VARIANT,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w", padx=(15,0), pady=(0,5))
        self.entry_password = ctk.CTkEntry(cred_grid, placeholder_text="********", show="*", height=40,
                                           border_color=COLOR_BORDER, fg_color=COLOR_CARD)
        self.entry_password.grid(row=1, column=1, sticky="ew", padx=(15,0), pady=(0,20))
        

        # --- Materias dinámicas ---
        materias_header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        materias_header.pack(fill="x", padx=40, pady=(20, 10))
        ctk.CTkLabel(materias_header, text="Carga de Materias",
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        self.btn_add = ctk.CTkButton(materias_header, text="+ Añadir Materia",
                                     fg_color="transparent", text_color=COLOR_PRIMARY,
                                     hover_color=COLOR_BORDER, font=ctk.CTkFont(weight="bold"),
                                     command=self.agregar_fila_materia)
        self.btn_add.pack(side="right")

        self.materias_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.materias_container.pack(fill="x", padx=40, pady=(0, 20))
        self.filas_materias = []
        # Cargar materias del catálogo para los ComboBox
        self.lista_materias = [m[1] for m in cargar_materias_catalogo()]
        self.agregar_fila_materia()   # una fila por defecto

        # --- Footer fijo con botones ---
        self.footer = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=80,
                                   corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)

        self.btn_guardar = ctk.CTkButton(self.footer, text="Guardar Docente",
                                         command=self.guardar_docente_desde_formulario,
                                         fg_color=COLOR_PRIMARY, height=40, width=150)
        self.btn_guardar.pack(side="right", padx=40, pady=18)

        self.btn_cancelar = ctk.CTkButton(self.footer, text="Cancelar",
                                          fg_color="transparent", text_color=COLOR_PRIMARY,
                                          border_width=1, border_color=COLOR_BORDER,
                                          hover_color=COLOR_BG, height=40,width=150,
                                          command=self.destroy)
        self.btn_cancelar.pack(side="right", padx=(0, 10), pady=18)

    # ---------- Métodos auxiliares ----------
    def agregar_fila_materia(self):
        fila = ctk.CTkFrame(self.materias_container, fg_color=COLOR_CARD,
                            border_width=1, border_color=COLOR_BORDER, corner_radius=8)
        fila.pack(fill="x", pady=6)
        fila.grid_columnconfigure(0, weight=4)
        fila.grid_columnconfigure(1, weight=2)
        fila.grid_columnconfigure(2, weight=1)
        fila.grid_columnconfigure(3, weight=1)
        fila.grid_columnconfigure(4, weight=0)

        # Cambio aquí: usar ComboBox para seleccionar materia del catálogo
        if self.lista_materias:
            entrada_nombre = ctk.CTkComboBox(fila, values=self.lista_materias, height=35,
                                            border_color=COLOR_BORDER, fg_color=COLOR_BG)
        else:
            entrada_nombre = ctk.CTkEntry(fila, placeholder_text="No hay materias en catálogo", height=35,
                                        border_color=COLOR_BORDER, fg_color=COLOR_BG, state="disabled")
        entrada_nombre.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        combo_grado = ctk.CTkComboBox(fila, values=["1er Año", "2do Año", "3er Año", "4to Año", "5to Año"],
                                    height=35, border_color=COLOR_BORDER, fg_color=COLOR_BG)
        combo_grado.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        entrada_seccion = ctk.CTkEntry(fila, placeholder_text="Sección", width=60, height=35,
                                    border_color=COLOR_BORDER, fg_color=COLOR_BG)
        entrada_seccion.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        entrada_horas = ctk.CTkEntry(fila, placeholder_text="Horas", width=60, height=35,
                                    border_color=COLOR_BORDER, fg_color=COLOR_BG)
        entrada_horas.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        btn_eliminar = ctk.CTkButton(fila, text="Borrar", width=60, height=32, fg_color="#ffdad6",
                                    text_color="#ba1a1a", hover_color="#ffb4ab",
                                    command=lambda f=fila: self.eliminar_fila(f))
        btn_eliminar.grid(row=0, column=4, padx=10, pady=10, sticky="e")

        self.filas_materias.append({
            "frame": fila,
            "nombre": entrada_nombre,
            "grado": combo_grado,
            "seccion": entrada_seccion,
            "horas": entrada_horas
        })
    def eliminar_fila(self, frame_a_eliminar):
        for item in self.filas_materias:
            if item["frame"] == frame_a_eliminar:
                self.filas_materias.remove(item)
                frame_a_eliminar.destroy()
                break

    def guardar_docente_desde_formulario(self):
        nombre = self.entry_nombre.get().strip()
        cedula = self.entry_cedula.get().strip()
        dia_libre = self.combo_dia.get()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        rol = self.rol_var.get()
        # El rol se puede usar después para crear usuario, pero Docente no lo requiere
        # rol = self.rol_var.get()

        if not nombre or not cedula:
            messagebox.showwarning("Campos vacíos", "Por favor, complete los campos de Nombre y Cédula.")
            return
        if not usuario or not password:
            messagebox.showwarning("Credenciales", "Debe definir un nombre de usuario y contraseña.")
            return

        # Verificar si ya existe el docente
        if existe_docente(cedula):
            if not messagebox.askyesno("Docente existente", f"Ya existe un docente con cédula {cedula}. ¿Desea actualizar sus datos?"):
                return

        # Recolectar materias
        materias_asignadas = []
        for item in self.filas_materias:
            nom_mat = item["nombre"].get().strip()
            grado = item["grado"].get()
            seccion = item["seccion"].get().strip()
            hrs_str = item["horas"].get().strip()
            if not nom_mat:
                continue
            if not seccion:
                seccion = "A"   # valor por defecto
            try:
                horas = float(hrs_str) if hrs_str else 0.0
            except ValueError:
                messagebox.showerror("Error", f"Horas inválidas para la materia '{nom_mat}'")
                return
            grado_num = grado.split()[0]
            id_seccion = f"{grado_num}{seccion}"
            # Crear objeto Materia (sin días asignados por ahora)
            materia = Materia(nom_mat, id_seccion, horas, [])
            materias_asignadas.append(materia)
            
        # Crear docente
        nuevo_docente = Docente(nombre=nombre, cedula=cedula, dia_libre=dia_libre)
        for mat in materias_asignadas:
            nuevo_docente.agregar_materia(mat)

        # Guardar en BD
        try:
            exito = guardar_docente(nuevo_docente)
            if not exito:
                messagebox.showerror("Error", "No se pudo guardar el docente en la base de datos.")
                return
            # Guardar usuario (si el docente se guardó bien)
            guardar_usuario_db(usuario, password, rol)
            messagebox.showinfo("Éxito", f"Docente {nombre} registrado correctamente.\nUsuario: {usuario} (rol: {rol})")
            if self.vista_docentes and hasattr(self.vista_docentes, "refrescar"):
                self.vista_docentes.refrescar()
            self.destroy()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error de Guardado", f"Ocurrió una excepción:\n{e}")
# ================================================================
# NUEVA CLASE: VENTANA DE REGISTRO DE MATERIA
# ================================================================
class RegistroMateriaVentana(ctk.CTkToplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("Añadir Nueva Materia")
        self.geometry("450x250")  # Tamaño más adecuado
        self.configure(fg_color="white")
        self.transient(parent)
        self.grab_set()

        # Formulario
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Nombre de la Materia", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0,5))
        self.entry_nombre = ctk.CTkEntry(frame, placeholder_text="Ej. Física, Literatura...", height=40)
        self.entry_nombre.pack(fill="x", pady=(0,20))

        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10,0))
        btn_guardar = ctk.CTkButton(btn_frame, text="Guardar Materia", fg_color=COLOR_PRIMARY, command=self.guardar)
        btn_guardar.pack(side="right", padx=(5,0))
        btn_cancelar = ctk.CTkButton(btn_frame, text="Cancelar", fg_color="transparent", text_color=COLOR_PRIMARY,
                                     border_width=1, border_color=COLOR_BORDER, command=self.destroy)
        btn_cancelar.pack(side="right")

    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Error", "Ingrese el nombre de la materia")
            return
        if guardar_materia_catalogo(nombre):
            messagebox.showinfo("Éxito", f"Materia '{nombre}' añadida al catálogo.")
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar la materia (puede que ya exista).")  
# ================================================================
# VISTA: GESTIÓN DE DOCENTES (Modificada)
# ================================================================
class DocentesVista(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(self.header, text="Gestión de Docentes",
                     font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        
        self.btn_registrar = ctk.CTkButton(
            self.header, text="+ Registrar Nuevo Docente",
            fg_color=COLOR_PRIMARY, height=40,
            command=self.abrir_formulario_registro
        ) 
        
            
        self.btn_registrar.pack(side="right")
        
        if Sesion.rol_actual == "Docente":
            self.btn_registrar.pack_forget()
        

        # Contenedor con scroll para la lista de docentes
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD,
                                                       border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Cargar los docentes al iniciar
        self.refrescar()

    def abrir_formulario_registro(self):
        RegistroDocenteVentana(self.winfo_toplevel(), self)

    def refrescar(self):
        """Recarga la lista de docentes desde la BD y la muestra"""
        # Limpiar contenido anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        sistema = cargar_datos_sistema()
        docentes = sistema.docentes

        if not docentes:
            ctk.CTkLabel(self.scrollable_frame,
                         text="No hay docentes registrados.",
                         font=ctk.CTkFont(size=14, slant="italic")).pack(pady=50)
            return

        for docente in docentes:
            frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)

            # Nombre y datos principales
            lbl_nombre = ctk.CTkLabel(frame,
                                      text=f"{docente.nombre} ({docente.cedula}) - Libre: {docente.dia_libre}",
                                      font=ctk.CTkFont(size=13))
            lbl_nombre.pack(anchor="w")

            # Materias
            materias_texto = ", ".join([f"{m.nombre} ({m.id_seccion})" for m in docente.materias])
            lbl_materias = ctk.CTkLabel(frame,
                                        text=f"Materias: {materias_texto if materias_texto else 'Ninguna'}",
                                        text_color="#44474e", font=ctk.CTkFont(size=11))
            lbl_materias.pack(anchor="w")

            # Línea separadora
            ctk.CTkFrame(self.scrollable_frame, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=10, pady=5)
# ================================================================
# VISTA: GESTIÓN DE MATERIAS
# ================================================================
class MateriasVista(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller

        # HEADER
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))
        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Catálogo de Materias", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Lista de asignaturas disponibles en la institución.", font=ctk.CTkFont(size=14), text_color="#44474e").pack(anchor="w")

        self.btn_agregar = ctk.CTkButton(self.header, text="+ Añadir Nueva Materia", fg_color=COLOR_PRIMARY, height=40, command=self.abrir_formulario)
        self.btn_agregar.pack(side="right")
        if Sesion.rol_actual == "Docente":
            self.btn_agregar.pack_forget()

        # Tabla
        self.table_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.table_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.materias = []
        self.cargar_datos()

    def cargar_datos(self):
        from data_base import cargar_materias_catalogo
        self.materias = cargar_materias_catalogo()
        self.mostrar_tabla()

    def mostrar_tabla(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not self.materias:
            ctk.CTkLabel(self.table_frame, text="No hay materias registradas.", font=ctk.CTkFont(size=16, slant="italic"), text_color="#74777f").pack(pady=100)
            return

        # Encabezado
        header_frame = ctk.CTkFrame(self.table_frame, fg_color="#f8fafc", height=40)
        header_frame.pack(fill="x")
        ctk.CTkLabel(header_frame, text="Materia", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_VARIANT).place(relx=0.05, rely=0.5, anchor="w")
        if Sesion.rol_actual != "Docente":
            ctk.CTkLabel(header_frame, text="Acciones", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_VARIANT).place(relx=0.85, rely=0.5, anchor="w")

        # Filas
        for idx, (mid, nombre) in enumerate(self.materias):
            row = ctk.CTkFrame(self.table_frame, fg_color="transparent", height=45)
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=nombre, font=ctk.CTkFont(size=13, weight="bold")).place(relx=0.05, rely=0.5, anchor="w")
            if Sesion.rol_actual != "Docente":
                btn_eliminar = ctk.CTkButton(row, text="Eliminar", width=60, height=28, fg_color="#ffdad6", text_color="#ba1a1a",
                                             hover_color="#ffb4ab", command=lambda m_id=mid: self.eliminar_materia(m_id))
                btn_eliminar.place(relx=0.85, rely=0.5, anchor="w")
            ctk.CTkFrame(self.table_frame, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=10)

    def eliminar_materia(self, materia_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta materia del catálogo?"):
            from data_base import eliminar_materia_catalogo
            eliminar_materia_catalogo(materia_id)
            self.cargar_datos()

    def abrir_formulario(self):
        RegistroMateriaVentana(self.winfo_toplevel(), self.cargar_datos)
# ================================================================
# VISTA: HORARIOS (convertida del diseño HTML / Tailwind)
# ================================================================
class HorariosVista(ctk.CTkScrollableFrame):
    SLOT_BG_PRIMARY = "#e8eef8"
    SLOT_BG_TERTIARY = "#e6f7f4"
    SLOT_BORDER_PRIMARY = COLOR_PRIMARY
    SLOT_BORDER_TERTIARY = "#3cafa2"
    EMPTY_SLOT_BG = "#f4f3f7"
    ROW_PATRIOT_BG = "#f0f4fa"
    ROW_RECESO_BG = "#efedf1"

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller
        self.horario_maestro = {}   # se cargará después

        # --- Barra superior ---
        top = ctk.CTkFrame(self, fg_color=COLOR_BG, border_width=0)
        top.pack(fill="x", padx=24, pady=(24, 16))

        left_top = ctk.CTkFrame(top, fg_color="transparent")
        left_top.pack(side="left", fill="y")
        ctk.CTkLabel(left_top, text="Horarios", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w")

        right_top = ctk.CTkFrame(top, fg_color="transparent")
        right_top.pack(side="right")
        
        self.btn_exportar = ctk.CTkButton(right_top, text="Exportar a PDF", fg_color="transparent",
                                  border_width=1, border_color=COLOR_PRIMARY, text_color=COLOR_PRIMARY,
                                  height=36, width=150, command=self._exportar_pdf_real)
        self.btn_exportar.pack(side="left", padx=(0, 8))

        self.btn_generar = ctk.CTkButton(right_top, text="Generar Horario", fg_color=COLOR_PRIMARY,
                                        text_color="white", height=36, width=150,
                                        command=self.ejecutar_generacion_horarios)
        self.btn_generar.pack(side="left", padx=(0, 16))
                
        if Sesion.rol_actual != "Administrativo":
            self.btn_exportar.configure(state="disabled", fg_color="gray")
            self.btn_generar.configure(state="disabled", fg_color="gray")

        sep = ctk.CTkFrame(right_top, width=1, height=28, fg_color=COLOR_BORDER)
        sep.pack(side="left", padx=(0, 16))

        user_box = ctk.CTkFrame(right_top, fg_color="transparent")
        user_box.pack(side="left")
        avatar = ctk.CTkFrame(user_box, width=32, height=32, corner_radius=16, fg_color="#d0e1fb")
        avatar.pack(side="left", padx=(0, 8))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="U", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(user_box, text="Usuario", font=ctk.CTkFont(size=14, weight="normal"),
                     text_color="#1a1b1e").pack(side="left")
        
        

        # --- Filtros ---
        filtros = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1,
                               border_color=COLOR_BORDER, corner_radius=12)
        filtros.pack(fill="x", padx=24, pady=(0, 16))
        inner_f = ctk.CTkFrame(filtros, fg_color="transparent")
        inner_f.pack(fill="x", padx=16, pady=16)
        inner_f.grid_columnconfigure(0, weight=1)
        inner_f.grid_columnconfigure(1, weight=1)
        inner_f.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(inner_f, text="VER POR SECCIÓN", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COLOR_TEXT_VARIANT).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.combo_seccion = ctk.CTkComboBox(inner_f, values=["Cargando..."], height=40,
                                             border_color=COLOR_BORDER)
        self.combo_seccion.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(inner_f, text="VER POR DOCENTE", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COLOR_TEXT_VARIANT).grid(row=0, column=1, sticky="w", padx=(0, 12))
        self.combo_docente = ctk.CTkComboBox(inner_f, values=["Cargando..."], height=40,
                                             border_color=COLOR_BORDER)
        self.combo_docente.grid(row=1, column=1, sticky="ew", padx=(0, 12))

        btn_aplicar = ctk.CTkButton(inner_f, text="Aplicar Filtros", command=self.aplicar_filtros,
                                    height=40, width=100)
        btn_aplicar.grid(row=1, column=2, sticky="e", padx=(10, 0))

        # --- Contenedor de la tabla (se limpiará y reconstruirá) ---
        self.table_wrap = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1,
                                       border_color=COLOR_BORDER, corner_radius=12)
        self.table_wrap.pack(fill="x", padx=24, pady=(0, 16))
        self._tabla = ctk.CTkFrame(self.table_wrap, fg_color=COLOR_CARD)
        self._tabla.pack(fill="x", padx=1, pady=1)

        # Cargar los datos iniciales
        self.actualizar_filtros()
        if self.combo_seccion.get():
            self.refrescar_tabla(seccion_filtro=self.combo_seccion.get())
        elif self.combo_docente.get():
            self.refrescar_tabla(docente_filtro=self.combo_docente.get())
        else:
            self.refrescar_tabla()

    # ---------- Métodos auxiliares ----------
    def actualizar_filtros(self):
        """Carga las secciones y docentes desde la BD para los combos."""
        import sqlite3
        conn = sqlite3.connect('horarios_liceo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT id_seccion FROM materias")
        secciones = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT nombre FROM docentes")
        docentes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        def seccion_key(orden):
            # sec ejemplo: "1A", "2B", "3C", etc.
            if orden and len(orden) >= 2:
                # Extraer parte numérica (primer carácter) y la letra
                try:
                    num = int(orden[0])  # el primer carácter es el número
                    letra = orden[1] if len(orden) > 1 else ''
                except ValueError:
                    num = 0
                    letra = orden
            else:
                num = 0
                letra = orden
            return (num, letra)
    
        secciones_ordenadas = sorted(secciones, key=seccion_key)
        
        # --- Ordenar docentes alfabéticamente (case-insensitive) ---
        docentes_ordenados = sorted(docentes, key=lambda x: x.lower())
            
            
        sec = ["Todos"] + secciones_ordenadas
        doc = ["Todos"] + docentes_ordenados
        
        self.combo_seccion.configure(values=sec)
        self.combo_docente.configure(values=doc)
        
        if secciones_ordenadas:
            self.combo_seccion.set(secciones_ordenadas[0])
        else:
            self.combo_seccion.set("Todos")
        if docentes_ordenados:
            self.combo_docente.set(docentes_ordenados[0])
        else:
            self.combo_docente.set("Todos")

    def aplicar_filtros(self):
        seccion = self.combo_seccion.get()
        docente = self.combo_docente.get()
        
        if seccion == "Todos" and docente == "Todos":
            messagebox.showwarning("Filtros inválidos", "No puede seleccionar 'Todos' en ambos filtros simultáneamente.\nElija un valor específico en al menos uno.")
            return
        # Si la cadena está vacía (no hay opciones), no aplicar filtro (mostrará vacío)
        if not seccion or seccion=="Todos":
            seccion = None
        if not docente or docente=="Todos":
            docente = None
        self.refrescar_tabla(seccion_filtro=seccion, docente_filtro=docente)
        
    def refrescar_tabla(self, seccion_filtro=None, docente_filtro=None):
        """Reconstruye toda la tabla con los horarios actuales (opcionalmente filtrados)."""
        # Limpiar tabla
        for widget in self._tabla.winfo_children():
            widget.destroy()
        #Si no hay foltro, se muestra un qviso
        if seccion_filtro is None and docente_filtro is None:
            # Mostrar un mensaje en la tabla
            for c in range(6):
                self._tabla.grid_columnconfigure(c, weight=1 if c > 0 else 0)
            f = ctk.CTkFrame(self._tabla, fg_color="transparent")
            f.grid(row=0, column=0, columnspan=6, sticky="nsew")
            ctk.CTkLabel(f, text="Seleccione una sección o docente para ver el horario.", font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        # Configurar columnas
        for c in range(6):
            self._tabla.grid_columnconfigure(c, weight=1 if c > 0 else 0, minsize=110 if c > 0 else 100)

        # Encabezados
        headers = ["Bloque", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        head_bg = "#efedf1"
        for col, h in enumerate(headers):
            f = ctk.CTkFrame(self._tabla, fg_color=head_bg, corner_radius=0)
            f.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)
            if col > 0:
                f.configure(border_width=1, border_color=COLOR_BORDER)
            ctk.CTkLabel(f, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLOR_TEXT_VARIANT).pack(pady=12, padx=8)

        # Cargar horario maestro desde BD
        self.horario_maestro = cargar_horario_maestro()

        # Dibujar filas de bloques
        r = 1
        r = self._fila_bloque_con_datos(r, "08:00", "09:10",
                                        self._obtener_celdas_dia("8:00-9:10", seccion_filtro, docente_filtro))
        r = self._fila_espacio_patriotico(r)
        r = self._fila_bloque_con_datos(r, "09:20", "10:30",
                                        self._obtener_celdas_dia("9:20-10:30", seccion_filtro, docente_filtro))
        r = self._fila_receso(r)
        r = self._fila_bloque_con_datos(r, "10:35", "11:45",
                                        self._obtener_celdas_dia("10:35-11:45", seccion_filtro, docente_filtro))
        self._fila_bloque_con_datos(r, "11:50", "13:00",
                                    self._obtener_celdas_dia("11:50-13:00", seccion_filtro, docente_filtro))

    def _obtener_celdas_dia(self, bloque, seccion_filtro, docente_filtro):
        """Retorna una lista de 5 elementos (cada uno: None o tupla con datos de clase)."""
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        celdas = []
        for dia in dias:
            clase = None
            for (d, b, sec), info in self.horario_maestro.items():
                if d == dia and b == bloque:
                    if seccion_filtro and sec != seccion_filtro:
                        continue
                    if docente_filtro and info['docente'] != docente_filtro:
                        continue
                    clase = (info['materia'], info['docente'], sec, "primary")
                    break
            celdas.append(clase)
        return celdas

    def _fila_bloque_con_datos(self, row, t1, t2, celdas_dia):
        """Dibuja una fila de horario con las celdas proporcionadas."""
        td = self._celda_tiempo(self._tabla, t1, t2)
        td.grid(row=row, column=0, sticky="nsew", padx=0, pady=0)
        self._tabla.grid_rowconfigure(row, weight=0, minsize=100)
        for i, data in enumerate(celdas_dia):
            col = i + 1
            cell = ctk.CTkFrame(self._tabla, fg_color=COLOR_CARD, corner_radius=0)
            cell.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            if data is None:
                self._celda_vacio(cell).pack(fill="both", expand=True)
            else:
                titulo, prof, lugar, estilo = data
                subs = [prof, lugar] if lugar else [prof]
                self._celda_clase(cell, titulo, subs, estilo).pack(fill="both", expand=True)
        return row + 1

    # ----- Métodos de dibujo de celdas (igual que antes) -----
    def _celda_tiempo(self, parent, inicio, fin):
        box = ctk.CTkFrame(parent, fg_color="#f4f3f7", corner_radius=0)
        ctk.CTkLabel(box, text=inicio, font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(10, 0))
        ctk.CTkLabel(box, text=fin, font=ctk.CTkFont(size=12),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(0, 10))
        return box

    def _celda_clase(self, parent, titulo, subtitulos, estilo):
        if estilo == "primary":
            bg, border, title_c, sub_c = self.SLOT_BG_PRIMARY, self.SLOT_BORDER_PRIMARY, COLOR_PRIMARY, "#38485d"
        else:
            bg, border, title_c, sub_c = self.SLOT_BG_TERTIARY, self.SLOT_BORDER_TERTIARY, "#005049", "#005049"
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        inner = ctk.CTkFrame(outer, fg_color=bg, corner_radius=8, border_width=0)
        inner.pack(fill="both", expand=True, padx=4, pady=6)
        stripe = ctk.CTkFrame(inner, width=4, fg_color=border, corner_radius=0)
        stripe.pack(side="left", fill="y", pady=0)
        content = ctk.CTkFrame(inner, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=(8, 10), pady=8)
        ctk.CTkLabel(content, text=titulo, font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=title_c).pack(anchor="w")
        for line in subtitulos:
            if line:
                ctk.CTkLabel(content, text=line, font=ctk.CTkFont(size=13),
                             text_color=sub_c).pack(anchor="w", pady=(2, 0))
        return outer

    def _celda_vacio(self, parent):
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        inner = ctk.CTkFrame(outer, fg_color=self.EMPTY_SLOT_BG, corner_radius=8,
                             border_width=1, border_color=COLOR_BORDER)
        inner.pack(fill="both", expand=True, padx=4, pady=6)
        ctk.CTkLabel(inner, text="+", font=ctk.CTkFont(size=20), text_color="#74777f").pack(pady=(12, 0))
        ctk.CTkLabel(inner, text="VACÍO", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#74777f").pack(pady=(0, 12))
        return outer

    def _fila_espacio_patriotico(self, row):
        left = ctk.CTkFrame(self._tabla, fg_color=self.ROW_PATRIOT_BG, corner_radius=0)
        left.grid(row=row, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="INTERMEDIO", font=ctk.CTkFont(size=11),
                     text_color=COLOR_PRIMARY).pack(pady=14, padx=12)
        span = ctk.CTkFrame(self._tabla, fg_color=self.ROW_PATRIOT_BG, corner_radius=0)
        span.grid(row=row, column=1, columnspan=5, sticky="nsew")
        pill = ctk.CTkFrame(span, fg_color=COLOR_PRIMARY, corner_radius=20)
        pill.pack(pady=12)
        ctk.CTkLabel(pill, text="  Espacio Patriótico  ", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="white").pack(padx=20, pady=8)
        return row + 1

    def _fila_receso(self, row):
        left = ctk.CTkFrame(self._tabla, fg_color="#e9e7eb", corner_radius=0)
        left.grid(row=row, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="RECESO", font=ctk.CTkFont(size=11),
                     text_color=COLOR_PRIMARY).pack(pady=12, padx=12)
        span = ctk.CTkFrame(self._tabla, fg_color=self.ROW_RECESO_BG, corner_radius=0)
        span.grid(row=row, column=1, columnspan=5, sticky="nsew")
        ctk.CTkLabel(span, text="Descanso General", font=ctk.CTkFont(size=14),
                     text_color=COLOR_TEXT_VARIANT).pack(pady=14)
        return row + 1

    def _tarjeta_info(self, master, col, titulo, texto, icon_bg, icon_fg):
        card = ctk.CTkFrame(master, fg_color="#f4f3f7", border_width=1,
                            border_color=COLOR_BORDER, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 12) if col < 2 else (0, 0))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=16)
        icon = ctk.CTkFrame(inner, width=40, height=40, corner_radius=8, fg_color=icon_bg)
        icon.pack(side="left", padx=(0, 12))
        icon.pack_propagate(False)
        ctk.CTkLabel(icon, text="i", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=icon_fg).place(relx=0.5, rely=0.5, anchor="center")
        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(txt, text=titulo, font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#1a1b1e").pack(anchor="w")
        ctk.CTkLabel(txt, text=texto, font=ctk.CTkFont(size=13),
                     text_color=COLOR_TEXT_VARIANT, wraplength=220).pack(anchor="w", pady=(4, 0))

    def _exportar_pdf_real(self):
        if not self.horario_maestro:
            messagebox.showerror("Error", "No hay horario generado para exportar. Primero genera un horario.")
            return
        try:
            exportar_a_pdf(self.horario_maestro, nombre_archivo="horario_liceo.pdf")
            messagebox.showinfo("Éxito", "PDF exportado como 'horario_liceo.pdf'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar PDF: {e}")

    def ejecutar_generacion_horarios(self):
        if Sesion.rol_actual != "Administrativo":
            messagebox.showerror("Acceso Denegado", "Solo el personal Administrativo puede generar horarios.")
            return
        sistema = cargar_datos_sistema()
        messagebox.showinfo("Procesando", "Generando el horario óptimo sin colisiones...")
        sistema.generar_horario()
        if sistema.horario_maestro:
            exito_bd = guardar_horario_maestro(sistema.horario_maestro)
            try:
                exportar_a_pdf(sistema.horario_maestro, nombre_archivo="horario_liceo.pdf")
                exito_pdf = True
            except Exception as e:
                exito_pdf = False
                print(f"Error al exportar PDF: {e}")
            if exito_bd and exito_pdf:
                messagebox.showinfo("Éxito", "¡Horario generado, guardado en BD y exportado a PDF!")
                self.refrescar_tabla()   # <--- ACTUALIZAR LA VISTA
            else:
                messagebox.showwarning("Advertencia", "El horario se calculó, pero hubo problemas al guardar o exportar.")
        else:
            messagebox.showerror("Error", "No se pudo generar el horario. Verifique las horas y días asignados.")
# ================================================================
# VISTA: PANEL PRINCIPAL (DASHBOARD)
# ================================================================
class DashboardVista(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller
        self.labels_valor = []  # Para almacenar los labels de los valores
        
        # Configuramos la cuadrícula principal del scroll
        self.grid_columnconfigure(0, weight=1)

        # 1. Header de Bienvenida
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(40, 20), padx=40)
        ctk.CTkLabel(self.header_frame, text="Bienvenido al Centro de Gestión",
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(self.header_frame, text="Supervise el progreso académico y gestione horarios institucionalmente.",
                     font=ctk.CTkFont(size=14),
                     text_color=COLOR_TEXT_VARIANT).pack(anchor="w")

        # 2. Bento Grid (Tarjetas de Resumen)
        self.bento_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bento_frame.grid(row=1, column=0, sticky="ew", pady=20, padx=30)
        self.bento_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # Crear tarjetas y guardar referencias a los labels de valor
        self.card_total_docentes = self.crear_card_resumen(self.bento_frame, "Total Docentes", None, None, 0)
        self.card_secciones_activas = self.crear_card_resumen(self.bento_frame, "Secciones Activas", None, None, 1)
        self.card_horarios_generados = self.crear_card_resumen(
            self.bento_frame, "Horarios Generados", None, None, 2,
            command=self._abrir_vista_horarios
        )

        # 3. Layout Inferior (Acciones y Actividad)
        self.layout_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.layout_inferior.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.layout_inferior.grid_columnconfigure(0, weight=1)
        self.layout_inferior.grid_columnconfigure(1, weight=2)

        self.col_izquierda = ctk.CTkFrame(self.layout_inferior, fg_color="transparent")
        self.col_izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.col_derecha = ctk.CTkFrame(self.layout_inferior, fg_color="transparent")
        self.col_derecha.grid(row=0, column=1, sticky="nsew")

        # Llenar contenido
        self.crear_seccion_acciones(self.col_izquierda)
        self.crear_seccion_actividad(self.col_derecha)

        # Cargar datos iniciales
        self.actualizar_dashboard()

    def crear_card_resumen(self, master, titulo, valor, trend, col, command=None):
        card = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, height=150)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12), text_color="#74777f").pack(pady=(20, 0), padx=20, anchor="w")

        if valor is None:
            # Placeholder mientras se carga
            lbl_valor = ctk.CTkLabel(card, text="--", font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_PRIMARY)
            lbl_valor.pack(pady=15, padx=20, anchor="w")
            # Guardamos la referencia para actualizar después
            self.labels_valor.append(lbl_valor)
        else:
            lbl_valor = ctk.CTkLabel(card, text=str(valor), font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_PRIMARY)
            lbl_valor.pack(pady=15, padx=20, anchor="w")
            if trend:
                ctk.CTkLabel(card, text=str(trend), font=ctk.CTkFont(size=11), text_color="#005049").pack(padx=20, anchor="w")

        if command:
            card.configure(cursor="hand2")
            def _on_click(event):
                command()
            card.bind("<Button-1>", _on_click)
            for child in card.winfo_children():
                child.bind("<Button-1>", _on_click)

        return lbl_valor  # Devolvemos el label para posible uso externo

    def actualizar_dashboard(self):
        """Consulta la BD y actualiza los valores de las tarjetas."""
        import sqlite3
        conn = sqlite3.connect('horarios_liceo.db')
        cursor = conn.cursor()
        
        # Total docentes
        cursor.execute("SELECT COUNT(*) FROM docentes")
        total_docentes = cursor.fetchone()[0]
        
        # Secciones activas (distintas id_seccion en materias)
        cursor.execute("SELECT COUNT(DISTINCT id_seccion) FROM materias")
        secciones_activas = cursor.fetchone()[0]
        
        # Horarios generados (cantidad de asignaciones en horarios_generados)
        cursor.execute("SELECT COUNT(*) FROM horarios_generados")
        horarios_generados = cursor.fetchone()[0]
        
        conn.close()
        
        # Actualizar los labels almacenados
        if len(self.labels_valor) >= 3:
            self.labels_valor[0].configure(text=str(total_docentes))
            self.labels_valor[1].configure(text=str(secciones_activas))
            self.labels_valor[2].configure(text=str(horarios_generados))

    def crear_seccion_acciones(self, master):
        # Acciones Rápidas
        frame_acciones = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_acciones.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(frame_acciones, text="Acciones Rápidas", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(15, 10))

        # Botón Generar Horario (solo visible para Administrativo)
        self.btn_generar = ctk.CTkButton(frame_acciones, text="+ Generar Nuevo Horario", fg_color=COLOR_PRIMARY, height=40, corner_radius=8,
                                         command=self._generar_horario_desde_dashboard)
        self.btn_generar.pack(fill="x", padx=20, pady=5)
        if Sesion.rol_actual != "Administrativo":
            self.btn_generar.configure(state="disabled", fg_color="gray")

        # Botón Exportar PDF Maestro (solo visible para Administrativo)
        self.btn_exportar = ctk.CTkButton(frame_acciones, text="Exportar PDF Maestro", fg_color="white", text_color=COLOR_PRIMARY,
                                          border_width=1, border_color=COLOR_PRIMARY, height=40, corner_radius=8,
                                          hover_color="#f1f5f9", command=self._exportar_pdf_desde_dashboard)
        self.btn_exportar.pack(fill="x", padx=20, pady=(5, 15))
        if Sesion.rol_actual != "Administrativo":
            self.btn_exportar.configure(state="disabled", fg_color="gray")

        # Widget de alertas 
        frame_alerta = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_alerta.pack(fill="x")
        ctk.CTkLabel(frame_alerta, text="Alertas de gestión", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(14, 4))

        from data_base import obtener_alertas
        alertas = obtener_alertas()
        if alertas:
            for alerta in alertas:
                ctk.CTkLabel(frame_alerta, text=f"• {alerta}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT, wraplength=300, justify="left").pack(anchor="w", padx=20, pady=(0,4))
        else:
            ctk.CTkLabel(frame_alerta, text="No hay alertas pendientes.", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT, justify="left", wraplength=320).pack(anchor="w", padx=20, pady=(0,14))

    def _generar_horario_desde_dashboard(self):
        """Ejecuta la generación de horario igual que en HorariosVista."""
        if Sesion.rol_actual != "Administrativo":
            messagebox.showerror("Acceso Denegado", "Solo el personal Administrativo puede generar horarios.")
            return
        sistema = cargar_datos_sistema()
        messagebox.showinfo("Procesando", "Generando el horario óptimo sin colisiones...")
        sistema.generar_horario()
        if sistema.horario_maestro:
            exito_bd = guardar_horario_maestro(sistema.horario_maestro)
            try:
                exportar_a_pdf(sistema.horario_maestro, nombre_archivo="horario_liceo.pdf")
                exito_pdf = True
            except Exception as e:
                exito_pdf = False
                print(f"Error al exportar PDF: {e}")
            if exito_bd and exito_pdf:
                messagebox.showinfo("Éxito", "¡Horario generado, guardado en BD y exportado a PDF!")
                # Refrescar dashboard
                self.actualizar_dashboard()
                # Opcional: notificar a la vista de horarios si está abierta (podría ser complejo)
            else:
                messagebox.showwarning("Advertencia", "El horario se calculó, pero hubo problemas al guardar o exportar.")
        else:
            messagebox.showerror("Error", "No se pudo generar el horario. Verifique las horas y días asignados.")

    def _exportar_pdf_desde_dashboard(self):
        horario = cargar_horario_maestro()
        if not horario:
            messagebox.showerror("Error", "No hay horario generado para exportar. Primero genera un horario.")
            return
        try:
            exportar_a_pdf(horario, nombre_archivo="horario_liceo.pdf")
            messagebox.showinfo("Éxito", "PDF exportado como 'horario_liceo.pdf'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar PDF: {e}")

    def crear_seccion_actividad(self, master):
        frame_tabla = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_tabla.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(frame_tabla, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="Actividad Reciente", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        
        headers_frame = ctk.CTkFrame(frame_tabla, fg_color="#f8fafc", height=35, corner_radius=0)
        headers_frame.pack(fill="x")
        lbl_config = {"font": ctk.CTkFont(size=11, weight="bold"), "text_color": COLOR_TEXT_VARIANT}
        ctk.CTkLabel(headers_frame, text="FECHA", **lbl_config).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(headers_frame, text="ACCIÓN", **lbl_config).place(relx=0.35, rely=0.5, anchor="w")
        ctk.CTkLabel(headers_frame, text="DETALLE", **lbl_config).place(relx=0.65, rely=0.5, anchor="w")
        
        logs = obtener_ultimos_logs(5)
        if not logs:
            vacio = ctk.CTkFrame(frame_tabla, fg_color="transparent")
            vacio.pack(fill="both", expand=True, padx=20, pady=24)
            ctk.CTkLabel(vacio, text="No hay actividad reciente.", font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_VARIANT, justify="center").pack(expand=True)
            return
        
        for idx, (fecha, accion, detalle, usuario) in enumerate(logs):
            fila = ctk.CTkFrame(frame_tabla, fg_color="transparent", height=40)
            fila.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(fila, text=fecha[:16], font=ctk.CTkFont(size=11)).place(relx=0.05, rely=0.5, anchor="w")
            ctk.CTkLabel(fila, text=accion, font=ctk.CTkFont(size=12, weight="bold")).place(relx=0.35, rely=0.5, anchor="w")
            ctk.CTkLabel(fila, text=detalle, font=ctk.CTkFont(size=11)).place(relx=0.65, rely=0.5, anchor="w")
            ctk.CTkFrame(frame_tabla, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=10)
        
    def _abrir_vista_horarios(self):
        if self.controller and hasattr(self.controller, "mostrar_horarios"):
            self.controller.mostrar_horarios()
        else:
            print("Error: No se pudo acceder a mostrar_horarios en el controlador")
# ================================================================
# APLICACIÓN BASE
# ================================================================
class EduManageApp(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra Lateral
        self.sidebar_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=COLOR_SIDEBAR, border_width=1, border_color=COLOR_BORDER)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Liceo Armando\nReverón", 
                                      font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=20, pady=30)

        # Botones
        self.btn_dashboard = self.crear_boton_menu("Panel Principal", 1, self.mostrar_dashboard, activo=True)
        self.btn_docentes = self.crear_boton_menu("Docentes", 2, self.mostrar_docentes)
        self.btn_materias = self.crear_boton_menu("Materias", 3, self.mostrar_materias)
        self.btn_horarios = self.crear_boton_menu("Horarios", 4, self.mostrar_horarios)
        self.btn_configuracion = self.crear_boton_menu("Configuración", 5, self.mostrar_configuracion)

        if Sesion.rol_actual == "Docente":
            self.btn_materias.grid_remove()
            self.btn_configuracion.grid_remove()
            
        # Espacio flexible para empujar "Cerrar sesión" al fondo
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.grid(row=6, column=0, sticky="nsew")

        self.btn_cerrar_sesion = ctk.CTkButton(
            self.sidebar_frame,
            text="Cerrar sesión",
            anchor="w",
            fg_color=COLOR_SIDEBAR,
            hover_color="#fee2e2",
            text_color="#b91c1c",
            border_width=1,
            border_color="#fca5a5",
            height=45,
            corner_radius=8,
            command=self.cerrar_sesion,
        )
        self.btn_cerrar_sesion.grid(row=7, column=0, padx=15, pady=(8, 18), sticky="ew")

        # Contenedor dinámico
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.contenedor_vistas.grid(row=0, column=1, sticky="nsew")
        self.contenedor_vistas.grid_columnconfigure(0, weight=1)
        self.contenedor_vistas.grid_rowconfigure(0, weight=1)

        self.mostrar_dashboard()

    def crear_boton_menu(self, texto, fila, comando, activo=False):
        # "transparent" en el menú lateral a veces no recibe clics (Windows / CTk); mismo tono que la barra.
        idle_bg = COLOR_PRIMARY if activo else COLOR_SIDEBAR
        idle_hover = "#1a3358" if activo else "#e0dfe3"
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=texto,
            anchor="w",
            fg_color=idle_bg,
            hover_color=idle_hover,
            text_color="white" if activo else "#505f76",
            height=45,
            corner_radius=8,
            command=comando,
        )
        btn.grid(row=fila, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def limpiar_vistas(self):
        for child in self.contenedor_vistas.winfo_children():
            child.destroy()

    def mostrar_dashboard(self):
        self.limpiar_vistas()
        view = DashboardVista(self.contenedor_vistas, self)
        view.grid(row=0, column=0, sticky="nsew")
        self.actualizar_estilo_botones(self.btn_dashboard)

    def mostrar_docentes(self):
        self.limpiar_vistas()
        view = DocentesVista(self.contenedor_vistas, self)
        view.grid(row=0, column=0, sticky="nsew")
        self.actualizar_estilo_botones(self.btn_docentes)
    
    def mostrar_materias(self):
        self.limpiar_vistas()
        view = MateriasVista(self.contenedor_vistas, self)
        view.grid(row=0, column=0, sticky="nsew")
        self.actualizar_estilo_botones(self.btn_materias)

    def mostrar_horarios(self):
        self.limpiar_vistas()
        try:
            view = HorariosVista(self.contenedor_vistas, self)
            view.grid(row=0, column=0, sticky="nsew")
            self.actualizar_estilo_botones(self.btn_horarios)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(
                "Horarios",
                "No se pudo cargar la vista de horarios.\n"
                f"Detalle: {e}\n\n"
                "Revisa la consola para el traceback completo.",
            )
            self.mostrar_dashboard()
            
    def mostrar_configuracion(self):
        self.limpiar_vistas()
        view = ConfiguracionVista(self.contenedor_vistas, self)
        view.grid(row=0, column=0, sticky="nsew")
        # No olvides actualizar el estilo del botón en el menú lateral
        self.actualizar_estilo_botones(self.btn_configuracion)

    def cerrar_sesion(self):
        if not messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión actual?"):
            return
        Sesion.cerrar_sesion()
        if self.controller is not None and hasattr(self.controller, "cambiar_vista"):
            self.controller.cambiar_vista("login_interfaz")

    def actualizar_estilo_botones(self, boton_activo):
        for btn in [
            self.btn_dashboard,
            self.btn_docentes,
            self.btn_materias,
            self.btn_horarios,
            self.btn_configuracion,
        ]:
            if btn == boton_activo:
                btn.configure(fg_color=COLOR_PRIMARY, text_color="white", hover_color="#1a3358")
            else:
                btn.configure(fg_color=COLOR_SIDEBAR, text_color="#505f76", hover_color="#e0dfe3")
        self.sidebar_frame.lift()