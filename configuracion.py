import customtkinter as ctk
from PIL import Image

# Reutilizamos tus constantes de color para mantener la armonía
COLOR_BG = "#faf9fd"
COLOR_PRIMARY = "#002046"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e3e2e6"
COLOR_TEXT_VARIANT = "#44474e"

class ConfiguracionVista(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        
        # --- HEADER DE LA VISTA ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(self.header, text="Configuración del Sistema", 
                     font=ctk.CTkFont(size=32, weight="bold"), 
                     text_color=COLOR_PRIMARY).pack(side="left")

        # --- SECCIÓN 1: PARÁMETROS ACADÉMICOS ---
        self.crear_seccion_parametros()

        # --- SECCIÓN 2: GESTIÓN DE USUARIOS ---
        self.crear_seccion_usuarios()

        # --- SECCIÓN 3: BASE DE DATOS Y SEGURIDAD ---
        self.crear_seccion_seguridad()

    def crear_seccion_parametros(self):
        container = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        container.grid(row=1, column=0, sticky="ew", padx=40, pady=10)
        
        # Título de sección
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(title_frame, text="Parámetros Académicos", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")

        # Grid de inputs
        grid_inputs = ctk.CTkFrame(container, fg_color="transparent")
        grid_inputs.pack(fill="x", padx=24, pady=(0, 24))
        
        campos = [("Año Escolar Actual", "2024-2025"), ("Duración Bloque (min)", "70"), ("Bloques por Día", "6")]
        
        for i, (label, value) in enumerate(campos):
            f = ctk.CTkFrame(grid_inputs, fg_color="transparent")
            f.pack(side="left", expand=True, fill="x", padx=10)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT).pack(anchor="w")
            entry = ctk.CTkEntry(f, height=35, fg_color="#faf9fd", border_color=COLOR_BORDER)
            entry.insert(0, value)
            entry.pack(fill="x", pady=5)

        ctk.CTkButton(container, text="Guardar Cambios", fg_color=COLOR_PRIMARY, height=35, width=150).pack(anchor="e", padx=24, pady=(0, 24))

    def crear_seccion_usuarios(self):
        container = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
        container.grid(row=2, column=0, sticky="ew", padx=40, pady=20)
        
        header_table = ctk.CTkFrame(container, fg_color="transparent")
        header_table.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(header_table, text="Gestión de Usuarios", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
        ctk.CTkButton(header_table, text="+ Nuevo Usuario", fg_color="transparent", text_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_PRIMARY, width=120).pack(side="right")

        # Simulación de Tabla
        table_frame = ctk.CTkFrame(container, fg_color=COLOR_BG, corner_radius=8)
        table_frame.pack(fill="x", padx=24, pady=(0, 24))
        
        headers = ["Usuario", "Rol", "Último Acceso"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_VARIANT).grid(row=0, column=i, padx=20, pady=10, sticky="w")

        # Fila de ejemplo
        ctk.CTkLabel(table_frame, text="admin", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        ctk.CTkLabel(table_frame, text="ADMINISTRADOR", font=ctk.CTkFont(size=10, weight="bold"), fg_color=COLOR_PRIMARY, text_color="white", corner_radius=4).grid(row=1, column=1, padx=20, pady=5)
        ctk.CTkLabel(table_frame, text="Hoy, 08:30 AM", font=ctk.CTkFont(size=12)).grid(row=1, column=2, padx=20, pady=5, sticky="w")

    def crear_seccion_seguridad(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 40))
        container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        # Card de Respaldo
        self.crear_card_accion(container, "Respaldo", "cloud_download", "Generar copia de seguridad.", 0)
        # Card de Restauración
        self.crear_card_accion(container, "Restauración", "settings_backup_restore", "Restaurar sistema.", 1)
        # Card Peligro (Limpieza)
        self.crear_card_accion(container, "Limpieza", "delete_sweep", "Eliminar todos los horarios.", 2, peligro=True)

    def crear_card_accion(self, master, titulo, icono, desc, col, peligro=False):
        color_accent = "#ba1a1a" if peligro else COLOR_PRIMARY
        card = ctk.CTkFrame(master, fg_color=COLOR_CARD, border_width=1, border_color="#ffdad6" if peligro else COLOR_BORDER, corner_radius=12)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14, weight="bold"), text_color=color_accent).pack(pady=(20, 5), padx=20, anchor="w")
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT, wraplength=150).pack(pady=5, padx=20, anchor="w")
        
        btn_color = "#ffdad6" if peligro else "#efedf1"
        btn_text = "#ba1a1a" if peligro else COLOR_PRIMARY
        
        ctk.CTkButton(card, text=f"Ejecutar {titulo}", fg_color=btn_color, text_color=btn_text, hover_color="#e3e2e6", height=32).pack(fill="x", padx=20, pady=20)