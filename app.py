import customtkinter as ctk
import traceback
from tkinter import messagebox
from PIL import Image
from auth import Sesion, requiere_admin
from configuracion import ConfiguracionVista

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
class RegistroDocenteVentana(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registrar Nuevo Docente")
        self.geometry("600x500")
        self.configure(fg_color="white")
        
        # Modal y prioridad
        self.transient(parent)
        self.grab_set()
        
        # Contenedor con Scroll
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        # Header de la ventana
        self.header = ctk.CTkFrame(self.main_container, fg_color="#faf9fd", height=100, corner_radius=0)
        self.header.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(self.header, text="Registrar Nuevo Docente",
                     font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=30, pady=(20, 5))

        # --- Formulario ---
        self.form_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=30, pady=20)
        self.form_frame.grid_columnconfigure((0, 1), weight=1)

        # Campo Nombre
        ctk.CTkLabel(self.form_frame, text="Nombre Completo", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w")
        self.entry_nombre = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. Ana Mendoza", height=40)
        self.entry_nombre.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        # Campo Cédula
        ctk.CTkLabel(self.form_frame, text="Número de Cédula", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w")
        self.entry_cedula = ctk.CTkEntry(self.form_frame, placeholder_text="V-00.000.000", height=40)
        self.entry_cedula.grid(row=1, column=1, sticky="ew")

        # Botones Footer
        self.btn_guardar = ctk.CTkButton(self, text="Guardar Docente", fg_color=COLOR_PRIMARY, command=self.destroy)
        self.btn_guardar.pack(side="bottom", pady=20)
        
# ================================================================
# NUEVA CLASE: VENTANA DE REGISTRO DE MATERIA
# ================================================================
class RegistroMateriaVentana(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Añadir Nueva Materia")
        self.geometry("500x450") # Tamaño más pequeño como en el HTML
        self.configure(fg_color="white")
        
        # Modal y prioridad
        self.transient(parent)
        self.grab_set()

        # Header de la ventana
        self.header = ctk.CTkFrame(self, fg_color="white", height=80, corner_radius=0)
        self.header.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(self.header, text="Añadir Nueva Materia",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=30, pady=20)

        # Línea divisoria
        ctk.CTkFrame(self, height=1, fg_color=COLOR_BORDER).pack(fill="x")

        # --- Formulario ---
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Campo Nombre
        ctk.CTkLabel(self.form_frame, text="Nombre de la Materia", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_nombre = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. Física, Literatura...", height=40)
        self.entry_nombre.pack(fill="x", pady=(0, 20))

        # Fila de Grado y Sección (Grid Layout)
        self.row_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.row_frame.pack(fill="x")
        self.row_frame.grid_columnconfigure((0, 1), weight=1)

        # Grado
        ctk.CTkLabel(self.row_frame, text="Grado/Año", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.combo_grado = ctk.CTkComboBox(self.row_frame, values=["1ero Año", "2do Año", "3ero Año", "4to Año", "5to Año"], height=40)
        self.combo_grado.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Sección
        ctk.CTkLabel(self.row_frame, text="Sección", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w", pady=(0, 5))
        self.combo_seccion = ctk.CTkComboBox(self.row_frame, values=["Sección A", "Sección B", "Sección C"], height=40)
        self.combo_seccion.grid(row=1, column=1, sticky="ew")

        # --- Botones Footer ---
        self.footer = ctk.CTkFrame(self, fg_color="#f4f3f7", height=80, corner_radius=0)
        self.footer.pack(fill="x", side="bottom")

        self.btn_guardar = ctk.CTkButton(self.footer, text="Guardar Materia", fg_color=COLOR_PRIMARY, text_color="white", height=40, font=ctk.CTkFont(weight="bold"), command=self.guardar_materia)
        self.btn_guardar.pack(side="right", padx=30, pady=20)
        
        self.btn_cancelar = ctk.CTkButton(self.footer, text="Cancelar", fg_color="transparent", text_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_BORDER, height=40, command=self.destroy)
        self.btn_cancelar.pack(side="right", padx=10, pady=20)

    def guardar_materia(self):
        nombre = self.entry_nombre.get()
        if not nombre:
            messagebox.showwarning("Error", "Por favor ingrese el nombre de la materia.")
            return
        
        messagebox.showinfo("Éxito", f"Materia {nombre} añadida correctamente.")
        self.destroy()
        
# ================================================================
# VISTA: GESTIÓN DE DOCENTES (Modificada)
# ================================================================
class DocentesVista(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        ctk.CTkLabel(self.header, text="Gestión de Docentes", 
                     font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        
        # --- CAMBIO AQUÍ: Creamos la variable self.btn_registrar y el comando ---
        self.btn_registrar = ctk.CTkButton(
            self.header, 
            text="+ Registrar Nuevo Docente", 
            fg_color=COLOR_PRIMARY, 
            height=40,
            command=self.abrir_formulario_registro # <--- Llama a la función de abajo
        )
        self.btn_registrar.pack(side="right")

        # 2. Contenedor de Tabla
        self.table_container = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)

        # Lógica de datos vacíos
        ctk.CTkLabel(self.table_container, 
                     text="No se encontraron docentes registrados.",
                     font=ctk.CTkFont(size=16, slant="italic"),
                     text_color="#74777f").pack(pady=100, fill="both")

    # --- NUEVA FUNCIÓN: Abre la ventana modal ---
    def abrir_formulario_registro(self):
        # winfo_toplevel() es para que la ventana sepa que la app principal es su "padre"
        RegistroDocenteVentana(self.winfo_toplevel())

# ================================================================
# VISTA: GESTIÓN DE MATERIAS
# ================================================================
class MateriasVista(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller
        
        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=40, pady=(40, 20))
        
        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Gestión de Materias", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Administre el catálogo de asignaturas, secciones y carga horaria institucional.", font=ctk.CTkFont(size=14), text_color="#44474e").pack(anchor="w")
        
        ctk.CTkButton(self.header, text="+ Añadir Nueva Materia", fg_color=COLOR_PRIMARY, height=40, 
                      command=self.abrir_formulario_materia).pack(side="right")

        # --- CONTENEDOR PRINCIPAL ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=3) # 75% Izquierda
        self.content_frame.grid_columnconfigure(1, weight=1) # 25% Derecha

        # ==========================================
        # COLUMNA IZQUIERDA: Filtros y Tabla
        # ==========================================
        self.left_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Filtros
        self.filter_frame = ctk.CTkFrame(self.left_panel, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.filter_frame.pack(fill="x", pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Buscar materia o docente...", width=250)
        self.search_entry.pack(side="left", padx=20, pady=15)
        
        self.combo_grado = ctk.CTkComboBox(self.filter_frame, values=["Todos los Grados", "1ero Año", "2do Año", "3ero Año", "4to Año", "5to Año"])
        self.combo_grado.pack(side="left", padx=10)
        
        self.combo_seccion = ctk.CTkComboBox(self.filter_frame, values=["Todas las Secciones", "Sección A", "Sección B", "Sección C"])
        self.combo_seccion.pack(side="left", padx=10)

        # Tabla de Materias (Limpia)
        self.table_container = ctk.CTkFrame(self.left_panel, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.table_container.pack(fill="both", expand=True)
        
        # Aquí llamarás a tu base de datos. Por ahora, estado vacío:
        self.materias_registradas = [] 

        if not self.materias_registradas:
            self.lbl_vacio = ctk.CTkLabel(self.table_container, 
                                          text="No hay materias registradas.\nSincronizando con base de datos...", 
                                          font=ctk.CTkFont(size=16, slant="italic"), 
                                          text_color="#74777f")
            self.lbl_vacio.pack(pady=100)
        else:
            self.dibujar_tabla_materias(self.materias_registradas)

        # ==========================================
        # COLUMNA DERECHA: Resumen Institucional
        # ==========================================
        self.right_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # Tarjeta 1: Resumen General (Valores en "--")
        self.resumen_card = ctk.CTkFrame(self.right_panel, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.resumen_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.resumen_card, text="Resumen Institucional", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Guardamos referencias a los labels para actualizarlos luego con self.label_total.configure(text="valor")
        self.crear_fila_resumen(self.resumen_card, "Total Materias", "--", COLOR_PRIMARY)
        self.crear_fila_resumen(self.resumen_card, "Horas Semanales", "--h", COLOR_PRIMARY)
        self.crear_fila_resumen(self.resumen_card, "Sin Docente", "--", "#ba1a1a")

        # Tarjeta 2: Horas por Grado (Barras en 0)
        self.horas_card = ctk.CTkFrame(self.right_panel, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        self.horas_card.pack(fill="x")
        
        ctk.CTkLabel(self.horas_card, text="Horas por Grado", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(20, 15))
        
        grados = ["1ero Año", "2do Año", "3ero Año", "4to Año", "5to Año"]
        for g in grados:
            self.crear_barra_progreso(self.horas_card, g, "0h", 0.0)

    # --- Funciones Auxiliares ---
    def abrir_formulario_materia(self):
        # Asegúrate de tener importada esta clase o creada
        # RegistroMateriaVentana(self.winfo_toplevel())
        pass
        
    def dibujar_tabla_materias(self, datos):
        # Limpiar tabla antes de redibujar
        for widget in self.table_container.winfo_children():
            widget.destroy()

        self.table_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        headers = ["MATERIA", "AÑO/SECCIÓN", "HORAS", "DOCENTE", "ESTADO"]
    
        for i, h in enumerate(headers):
            ctk.CTkLabel(self.table_container, text=h, font=ctk.CTkFont(size=11, weight="bold"), text_color="#74777f").grid(row=0, column=i, pady=15, padx=10, sticky="w")
        
        for idx, m in enumerate(datos, start=1):
            ctk.CTkLabel(self.table_container, text=m["nombre"], font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY).grid(row=idx, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(self.table_container, text=m["seccion"], text_color="#44474e").grid(row=idx, column=1, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(self.table_container, text=m["horas"]).grid(row=idx, column=2, padx=10, pady=10, sticky="w")
            
            docente_color = "#ba1a1a" if m["docente"] == "Sin asignar" else "#44474e"
            ctk.CTkLabel(self.table_container, text=m["docente"], text_color=docente_color).grid(row=idx, column=3, padx=10, pady=10, sticky="w")
            
            bg_color = "#d6e3ff" if m["estado"] == "Cubierta" else "#ffdad6"
            txt_color = COLOR_PRIMARY if m["estado"] == "Cubierta" else "#ba1a1a"
            badge = ctk.CTkLabel(self.table_container, text=m["estado"], fg_color=bg_color, text_color=txt_color, corner_radius=5, width=70, font=ctk.CTkFont(size=10, weight="bold"))
            badge.grid(row=idx, column=4, padx=10, pady=10, sticky="w")

    def crear_fila_resumen(self, master, titulo, valor, color_valor):
        fila = ctk.CTkFrame(master, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(fila, text=titulo, text_color="#44474e").pack(side="left")
        lbl_valor = ctk.CTkLabel(fila, text=valor, font=ctk.CTkFont(weight="bold"), text_color=color_valor)
        lbl_valor.pack(side="right")
        ctk.CTkFrame(master, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=20, pady=5)

    def crear_barra_progreso(self, master, titulo, valor, porcentaje):
        fila = ctk.CTkFrame(master, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=8)
        
        text_frame = ctk.CTkFrame(fila, fg_color="transparent")
        text_frame.pack(fill="x")
        ctk.CTkLabel(text_frame, text=titulo, font=ctk.CTkFont(size=12), text_color="#44474e").pack(side="left")
        ctk.CTkLabel(text_frame, text=valor, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PRIMARY).pack(side="right")
        
        prog = ctk.CTkProgressBar(fila, height=6, fg_color="#e3e2e6", progress_color=COLOR_PRIMARY)
        prog.pack(fill="x", pady=(5, 0))
        prog.set(porcentaje)


# ================================================================
# VISTA: HORARIOS (convertida del diseño HTML / Tailwind)
# ================================================================
class HorariosVista(ctk.CTkScrollableFrame):
    """Misma base que MateriasVista (CTkScrollableFrame): el padre la rellena con grid sticky nsew."""

    SLOT_BG_PRIMARY = "#e8eef8"
    SLOT_BG_TERTIARY = "#e6f7f4"
    SLOT_BORDER_PRIMARY = COLOR_PRIMARY
    SLOT_BORDER_TERTIARY = "#3cafa2"
    EMPTY_SLOT_BG = "#f4f3f7"
    ROW_PATRIOT_BG = "#f0f4fa"
    ROW_RECESO_BG = "#efedf1"
    _VACIOS_5 = [None, None, None, None, None]

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller

        # --- Barra superior (TopAppBar) ---
        top = ctk.CTkFrame(self, fg_color=COLOR_BG, border_width=0)
        top.pack(fill="x", padx=24, pady=(24, 16))

        left_top = ctk.CTkFrame(top, fg_color="transparent")
        left_top.pack(side="left", fill="y")
        ctk.CTkLabel(
            left_top,
            text="Horarios",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(anchor="w")

        right_top = ctk.CTkFrame(top, fg_color="transparent")
        right_top.pack(side="right")

        ctk.CTkButton(
            right_top,
            text="Exportar a PDF",
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_PRIMARY,
            text_color=COLOR_PRIMARY,
            height=36,
            width=150,
            command=self._exportar_pdf,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            right_top,
            text="Generar Horario",
            fg_color=COLOR_PRIMARY,
            text_color="white",
            height=36,
            width=150,
            command=self._generar_horario,
        ).pack(side="left", padx=(0, 16))

        sep = ctk.CTkFrame(right_top, width=1, height=28, fg_color=COLOR_BORDER)
        sep.pack(side="left", padx=(0, 16))

        user_box = ctk.CTkFrame(right_top, fg_color="transparent")
        user_box.pack(side="left")
        avatar = ctk.CTkFrame(user_box, width=32, height=32, corner_radius=16, fg_color="#d0e1fb")
        avatar.pack(side="left", padx=(0, 8))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="U", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY).place(
            relx=0.5, rely=0.5, anchor="center"
        )
        ctk.CTkLabel(user_box, text="Usuario", font=ctk.CTkFont(size=14, weight="normal"), text_color="#1a1b1e").pack(
            side="left"
        )

        # --- Filtros ---
        filtros = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        filtros.pack(fill="x", padx=24, pady=(0, 16))
        inner_f = ctk.CTkFrame(filtros, fg_color="transparent")
        inner_f.pack(fill="x", padx=16, pady=16)
        inner_f.grid_columnconfigure(0, weight=1)
        inner_f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            inner_f,
            text="VER POR SECCIÓN",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_TEXT_VARIANT,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.combo_seccion = ctk.CTkComboBox(
            inner_f,
            values=["Vacío"],
            height=40,
            border_color=COLOR_BORDER,
        )
        self.combo_seccion.set("Vacío")
        self.combo_seccion.grid(row=1, column=0, sticky="ew", padx=(0, 12))

        ctk.CTkLabel(
            inner_f,
            text="VER POR DOCENTE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_TEXT_VARIANT,
        ).grid(row=0, column=1, sticky="w", padx=(0, 12))
        self.combo_docente = ctk.CTkComboBox(
            inner_f,
            values=["Vacío"],
            height=40,
            border_color=COLOR_BORDER,
        )
        self.combo_docente.set("Vacío")
        self.combo_docente.grid(row=1, column=1, sticky="ew", padx=(0, 12))

        btn_filtros = ctk.CTkButton(
            inner_f,
            text="Más Filtros",
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_VARIANT,
            height=40,
            width=130,
            command=self._mas_filtros,
        )
        btn_filtros.grid(row=1, column=2, sticky="e")

        # --- Tabla de horarios ---
        table_wrap = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        table_wrap.pack(fill="x", padx=24, pady=(0, 16))
        self._tabla = ctk.CTkFrame(table_wrap, fg_color=COLOR_CARD)
        self._tabla.pack(fill="x", padx=1, pady=1)
        for c in range(6):
            self._tabla.grid_columnconfigure(c, weight=1 if c > 0 else 0, minsize=110 if c > 0 else 100)

        headers = ["Bloque", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        head_bg = "#efedf1"
        for col, h in enumerate(headers):
            f = ctk.CTkFrame(self._tabla, fg_color=head_bg, corner_radius=0)
            f.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)
            if col > 0:
                f.configure(border_width=1, border_color=COLOR_BORDER)
            ctk.CTkLabel(
                f,
                text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_TEXT_VARIANT,
            ).pack(pady=12, padx=8)

        r = 1
        r = self._fila_bloque(r, "08:00", "09:10", list(self._VACIOS_5))
        r = self._fila_espacio_patriotico(r)
        r = self._fila_bloque(r, "09:20", "10:30", list(self._VACIOS_5))
        r = self._fila_receso(r)
        r = self._fila_bloque(r, "10:35", "11:45", list(self._VACIOS_5))
        self._fila_bloque(r, "11:50", "13:00", list(self._VACIOS_5))

        # --- Leyenda / tarjetas inferiores ---
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=24, pady=(0, 32))
        legend.grid_columnconfigure((0, 1, 2), weight=1)

        self._tarjeta_info(
            legend,
            0,
            "Información de Bloques",
            "Sin datos: aún no hay información de bloques configurada.",
            icon_bg="#1b365d",
            icon_fg="#87a0cd",
        )
        self._tarjeta_info(
            legend,
            1,
            "Estado de Carga",
            "Sin datos: no hay información de carga horaria.",
            icon_bg="#3cafa2",
            icon_fg="white",
        )
        self._tarjeta_info(
            legend,
            2,
            "Última Modificación",
            "Sin datos: no hay modificaciones registradas.",
            icon_bg="#d0e1fb",
            icon_fg=COLOR_PRIMARY,
        )

    def _exportar_pdf(self):
        messagebox.showinfo("Exportar", "Exportación a PDF (pendiente de integrar con el módulo existente).")

    def _generar_horario(self):
        messagebox.showinfo("Generar", "Generación de horario (pendiente de conectar con la lógica del sistema).")

    def _mas_filtros(self):
        messagebox.showinfo("Filtros", "Más filtros próximamente.")

    def _celda_tiempo(self, parent, inicio, fin):
        box = ctk.CTkFrame(parent, fg_color="#f4f3f7", corner_radius=0)
        ctk.CTkLabel(box, text=inicio, font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(
            anchor="w", padx=12, pady=(10, 0)
        )
        ctk.CTkLabel(box, text=fin, font=ctk.CTkFont(size=12), text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(0, 10))
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
        ctk.CTkLabel(content, text=titulo, font=ctk.CTkFont(size=16, weight="bold"), text_color=title_c).pack(anchor="w")
        for line in subtitulos:
            if line:
                ctk.CTkLabel(content, text=line, font=ctk.CTkFont(size=13), text_color=sub_c).pack(anchor="w", pady=(2, 0))
        return outer

    def _celda_vacio(self, parent):
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        inner = ctk.CTkFrame(
            outer,
            fg_color=self.EMPTY_SLOT_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        inner.pack(fill="both", expand=True, padx=4, pady=6)
        ctk.CTkLabel(inner, text="+", font=ctk.CTkFont(size=20), text_color="#74777f").pack(pady=(12, 0))
        ctk.CTkLabel(
            inner,
            text="VACÍO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#74777f",
        ).pack(pady=(0, 12))
        return outer

    def _fila_bloque(self, row, t1, t2, celdas_dia):
        """celdas_dia: lista de 5 elementos: None (vacío) o (titulo, prof, lugar, 'primary'|'tertiary')."""
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
                subs = []
                if prof:
                    subs.append(prof)
                if lugar:
                    subs.append(lugar)
                self._celda_clase(cell, titulo, subs, estilo).pack(fill="both", expand=True)
        return row + 1

    def _fila_espacio_patriotico(self, row):
        left = ctk.CTkFrame(self._tabla, fg_color=self.ROW_PATRIOT_BG, corner_radius=0)
        left.grid(row=row, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="INTERMEDIO", font=ctk.CTkFont(size=11), text_color=COLOR_PRIMARY).pack(pady=14, padx=12)

        span = ctk.CTkFrame(self._tabla, fg_color=self.ROW_PATRIOT_BG, corner_radius=0)
        span.grid(row=row, column=1, columnspan=5, sticky="nsew")
        pill = ctk.CTkFrame(span, fg_color=COLOR_PRIMARY, corner_radius=20)
        pill.pack(pady=12)
        ctk.CTkLabel(
            pill,
            text="  Espacio Patriótico  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
        ).pack(padx=20, pady=8)
        return row + 1

    def _fila_receso(self, row):
        left = ctk.CTkFrame(self._tabla, fg_color="#e9e7eb", corner_radius=0)
        left.grid(row=row, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="RECESO", font=ctk.CTkFont(size=11), text_color=COLOR_PRIMARY).pack(pady=12, padx=12)

        span = ctk.CTkFrame(self._tabla, fg_color=self.ROW_RECESO_BG, corner_radius=0)
        span.grid(row=row, column=1, columnspan=5, sticky="nsew")
        ctk.CTkLabel(
            span,
            text="Descanso General",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_VARIANT,
        ).pack(pady=14)
        return row + 1

    def _tarjeta_info(self, master, col, titulo, texto, icon_bg, icon_fg):
        card = ctk.CTkFrame(master, fg_color="#f4f3f7", border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 12) if col < 2 else (0, 0))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=16)
        icon = ctk.CTkFrame(inner, width=40, height=40, corner_radius=8, fg_color=icon_bg)
        icon.pack(side="left", padx=(0, 12))
        icon.pack_propagate(False)
        ctk.CTkLabel(icon, text="i", font=ctk.CTkFont(size=16, weight="bold"), text_color=icon_fg).place(
            relx=0.5, rely=0.5, anchor="center"
        )
        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(txt, text=titulo, font=ctk.CTkFont(size=16, weight="bold"), text_color="#1a1b1e").pack(anchor="w")
        ctk.CTkLabel(txt, text=texto, font=ctk.CTkFont(size=13), text_color=COLOR_TEXT_VARIANT, wraplength=220).pack(
            anchor="w", pady=(4, 0)
        )


# ================================================================
# VISTA: PANEL PRINCIPAL (DASHBOARD)
# ================================================================
class DashboardVista(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller
        
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

        self.crear_card_resumen(self.bento_frame, "Total Docentes", None, None, 0)
        self.crear_card_resumen(self.bento_frame, "Secciones Activas", None, None, 1)
        self.crear_card_resumen(
            self.bento_frame,
            "Horarios Generados",
            None,
            None,
            2,
            command=self._abrir_vista_horarios,
        )

        # 3. Layout Inferior (Acciones y Actividad)
        # Cambiamos pack por grid para no romper la interfaz
        self.layout_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.layout_inferior.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.layout_inferior.grid_columnconfigure(0, weight=1) # Columna acciones (más estrecha)
        self.layout_inferior.grid_columnconfigure(1, weight=2) # Columna tabla (más ancha)

        # Columna Izquierda: Acciones Rápidas y Alertas
        self.col_izquierda = ctk.CTkFrame(self.layout_inferior, fg_color="transparent")
        self.col_izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Columna Derecha: Actividad Reciente
        self.col_derecha = ctk.CTkFrame(self.layout_inferior, fg_color="transparent")
        self.col_derecha.grid(row=0, column=1, sticky="nsew")

        # Llenar contenido
        self.crear_seccion_acciones(self.col_izquierda)
        self.crear_seccion_actividad(self.col_derecha)

    def crear_seccion_acciones(self, master):
        # Acciones Rápidas
        frame_acciones = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_acciones.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(frame_acciones, text="Acciones Rápidas", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(15, 10))

        btn_generar = ctk.CTkButton(frame_acciones, text="+ Generar Nuevo Horario", fg_color=COLOR_PRIMARY, height=40, corner_radius=8)
        btn_generar.pack(fill="x", padx=20, pady=5)

        btn_pdf = ctk.CTkButton(frame_acciones, text="Exportar PDF Maestro", fg_color="white", text_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_PRIMARY, height=40, corner_radius=8, hover_color="#f1f5f9")
        btn_pdf.pack(fill="x", padx=20, pady=(5, 15))

        # Widget de alertas (vacío hasta conectar con la BD)
        frame_alerta = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_alerta.pack(fill="x")

        ctk.CTkLabel(
            frame_alerta,
            text="Alertas de gestión",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(
            frame_alerta,
            text="Sin datos. Las alertas se mostrarán al sincronizar con la base de datos.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_VARIANT,
            justify="left",
            wraplength=320,
        ).pack(anchor="w", padx=20, pady=(0, 14))

    def crear_seccion_actividad(self, master):
        frame_tabla = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        frame_tabla.pack(fill="both", expand=True)

        header = ctk.CTkFrame(frame_tabla, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="Actividad Reciente", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        
        headers_frame = ctk.CTkFrame(frame_tabla, fg_color="#f8fafc", height=35, corner_radius=0)
        headers_frame.pack(fill="x")
        
        lbl_config = {"font": ctk.CTkFont(size=11, weight="bold"), "text_color": COLOR_TEXT_VARIANT}
        ctk.CTkLabel(headers_frame, text="ACCIÓN", **lbl_config).place(relx=0.05, rely=0.5, anchor="w")
        ctk.CTkLabel(headers_frame, text="DETALLE", **lbl_config).place(relx=0.45, rely=0.5, anchor="w")
        ctk.CTkLabel(headers_frame, text="ESTADO", **lbl_config).place(relx=0.85, rely=0.5, anchor="w")

        vacio = ctk.CTkFrame(frame_tabla, fg_color="transparent")
        vacio.pack(fill="both", expand=True, padx=20, pady=24)
        ctk.CTkLabel(
            vacio,
            text="Sin actividad registrada.\nLos movimientos aparecerán al conectar con la base de datos.",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_VARIANT,
            justify="center",
        ).pack(expand=True)

    def agregar_fila_actividad(self, master, titulo, subtitulo, detalle, estado):
        """Reservado para cuando se conecte la BD (llenar la tabla de actividad)."""
        fila = ctk.CTkFrame(master, fg_color="transparent", height=60)
        fila.pack(fill="x", padx=5)

        ctk.CTkLabel(fila, text=titulo, font=ctk.CTkFont(size=12, weight="bold")).place(relx=0.05, rely=0.35, anchor="w")
        ctk.CTkLabel(fila, text=subtitulo, font=ctk.CTkFont(size=10), text_color=COLOR_TEXT_VARIANT).place(relx=0.05, rely=0.65, anchor="w")
        ctk.CTkLabel(fila, text=detalle, font=ctk.CTkFont(size=12)).place(relx=0.45, rely=0.5, anchor="w")

        color_badge = "#d0e1fb" if estado == "Aplicado" else "#fee2e2"
        badge = ctk.CTkLabel(
            fila,
            text=estado,
            fg_color=color_badge,
            text_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=6,
            width=70,
        )
        badge.place(relx=0.92, rely=0.5, anchor="e")

        ctk.CTkFrame(master, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=20)

    def _abrir_vista_horarios(self):
        if self.controller and hasattr(self.controller, "mostrar_horarios"):
            self.controller.mostrar_horarios()
        else:
            print("Error: No se pudo acceder a mostrar_horarios en el controlador")

    def crear_card_resumen(self, master, titulo, valor, trend, col, command=None):
        card = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, height=150)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12), text_color="#74777f").pack(pady=(20, 0), padx=20, anchor="w")

        if not valor:
            ctk.CTkLabel(
                card,
                text="Sin datos",
                font=ctk.CTkFont(size=16, slant="italic"),
                text_color="#9da3ae",
            ).pack(pady=15, padx=20, anchor="w")
            ctk.CTkLabel(
                card,
                text="Se completará al conectar con la base de datos.",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_VARIANT,
                wraplength=200,
                justify="left",
            ).pack(padx=20, pady=(0, 12), anchor="w")
        else:
            ctk.CTkLabel(card, text=str(valor), font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_PRIMARY).pack(padx=20, anchor="w")
            if trend:
                ctk.CTkLabel(card, text=str(trend), font=ctk.CTkFont(size=11), text_color="#005049").pack(padx=20, anchor="w")

        if command:
            card.configure(cursor="hand2")
            # Handler mejorado para capturar el evento de clic
            def _on_click(event):
                command()

            card.bind("<Button-1>", _on_click)
            # Aseguramos que los hijos también disparen el comando
            for child in card.winfo_children():
                child.bind("<Button-1>", _on_click)

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