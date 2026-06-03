import customtkinter as ctk
from PIL import Image
import sqlite3
from auth import requiere_admin,Sesion
from tkinter import messagebox
from data_base import obtener_configuracion,guardar_configuracion
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
        if Sesion.rol_actual == "Docente":
            ctk.CTkLabel(self, text="Acceso restringido a configuración.", font=ctk.CTkFont(size=16)).pack(pady=100)
            return
        
        
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
        
        
        
        self.config_entries = {}
        campos = [
            ("Año Escolar Actual", "anio_escolar"),
            ("Duración Bloque (min)", "duracion_bloque"),
            ("Bloques por Día", "bloques_por_dia")
        ]
        for i, (label, clave) in enumerate(campos):
            f = ctk.CTkFrame(grid_inputs, fg_color="transparent")
            f.pack(side="left", expand=True, fill="x", padx=10)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT).pack(anchor="w")
            entry = ctk.CTkEntry(f, height=35, fg_color="#faf9fd", border_color=COLOR_BORDER)
            entry.insert(0, obtener_configuracion(clave) or "")
            entry.pack(fill="x", pady=5)
            self.config_entries[clave] = entry

        btn_guardar = ctk.CTkButton(container, text="Guardar Cambios", fg_color=COLOR_PRIMARY, height=35, width=150,
                                    command=self.guardar_configuracion)
        btn_guardar.pack(anchor="e", padx=24, pady=(0, 24))

    def crear_seccion_usuarios(self):
            container = ctk.CTkFrame(self, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=12)
            container.grid(row=2, column=0, sticky="ew", padx=40, pady=20)

            header_table = ctk.CTkFrame(container, fg_color="transparent")
            header_table.pack(fill="x", padx=24, pady=20)
            ctk.CTkLabel(header_table, text="Gestión de Usuarios", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left")
            btn_nuevo = ctk.CTkButton(header_table, text="+ Nuevo Usuario", fg_color="transparent", text_color=COLOR_PRIMARY,
                                    border_width=1, border_color=COLOR_PRIMARY, width=120,
                                    command=self.abrir_nuevo_usuario)
            btn_nuevo.pack(side="right")

            # Contenedor para la tabla (scrollable si hay muchos)
            self.usuarios_frame = ctk.CTkScrollableFrame(container, fg_color=COLOR_BG, corner_radius=8, height=200)
            self.usuarios_frame.pack(fill="x", padx=24, pady=(0, 24))

            self.cargar_usuarios()

    def cargar_usuarios(self):
            from data_base import obtener_usuarios
            for widget in self.usuarios_frame.winfo_children():
                widget.destroy()
            usuarios = obtener_usuarios()
            if not usuarios:
                ctk.CTkLabel(self.usuarios_frame, text="No hay usuarios registrados.", font=ctk.CTkFont(size=12)).pack(pady=20)
                return
            # Encabezados
            headers = ["Usuario", "Rol"]
            for i, h in enumerate(headers):
                ctk.CTkLabel(self.usuarios_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT_VARIANT).grid(row=0, column=i, padx=20, pady=10, sticky="w")
            for idx, (usuario, rol) in enumerate(usuarios, start=1):
                ctk.CTkLabel(self.usuarios_frame, text=usuario, font=ctk.CTkFont(size=13)).grid(row=idx, column=0, padx=20, pady=5, sticky="w")
                rol_label = ctk.CTkLabel(self.usuarios_frame, text=rol.upper(), font=ctk.CTkFont(size=10, weight="bold"),
                                        fg_color=COLOR_PRIMARY if rol == "Administrativo" else "#3cafa2",
                                        text_color="white", corner_radius=4)
                rol_label.grid(row=idx, column=1, padx=20, pady=5, sticky="w")

    def abrir_nuevo_usuario(self):
            NuevoUsuarioVentana(self, self.cargar_usuarios)
            
            
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
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14, weight="bold"), text_color=color_accent).pack(pady=(20,5), padx=20, anchor="w")
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_VARIANT, wraplength=150).pack(pady=5, padx=20, anchor="w")
        btn_color = "#ffdad6" if peligro else "#efedf1"
        btn_text = "#ba1a1a" if peligro else COLOR_PRIMARY
        btn = ctk.CTkButton(card, text=f"Ejecutar {titulo}", fg_color=btn_color, text_color=btn_text, hover_color="#e3e2e6", height=32,
                            command=lambda t=titulo: self.ejecutar_accion(t))
        btn.pack(fill="x", padx=20, pady=20)

    """ Ejecutar_accion antiguo para referencia
    def ejecutar_accion(self, accion):
        if accion == "Limpieza":
            self.vaciar_horarios()
        elif accion == "Respaldo":
            self.respaldar_bd()
        elif accion == "Restauración":
            self.restaurar_bd()""" 
    
    def ejecutar_accion(self, accion):
        acciones = {
            "Limpieza": self.vaciar_horarios,
            "Respaldo": self.respaldar_bd,
            "Restauración": self.restaurar_bd,
        }
        metodo = acciones.get(accion)
        if metodo:
            metodo()
        else:
            messagebox.showerror("Error", f"Acción no reconocida: {accion}")
    
    def vaciar_horarios(self):
        if not messagebox.askyesno("Confirmar", "¿Eliminar todos los horarios generados? No se puede deshacer."):
            return
        import sqlite3
        conn = sqlite3.connect('horarios_liceo.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM horarios_generados')
        conn.commit()
        conn.close()
        messagebox.showinfo("Limpieza", "Todos los horarios han sido eliminados.")

    def respaldar_bd(self):
        import shutil, datetime
        try:
            backup_name = f"backup_horarios_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy('horarios_liceo.db', backup_name)
            messagebox.showinfo("Respaldo", f"Respaldo creado: {backup_name}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo respaldar: {e}")

    def restaurar_bd(self):
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(title="Seleccionar archivo de respaldo", filetypes=[("Base de datos", "*.db")])
        if archivo:
            import shutil
            try:
                shutil.copy(archivo, 'horarios_liceo.db')
                messagebox.showinfo("Restauración", "Base de datos restaurada. Reinicie la aplicación para ver los cambios.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restaurar: {e}")
    
    def guardar_configuracion(self):
        for clave, entry in self.config_entries.items():
            guardar_configuracion(clave, entry.get().strip())
        messagebox.showinfo("Configuración", "Parámetros guardados correctamente.")

class NuevoUsuarioVentana(ctk.CTkToplevel):
    def __init__(self, parent, callback_refrescar):
        super().__init__(parent)
        self.callback = callback_refrescar
        self.title("Registrar Nuevo Usuario")
        self.geometry("400x350")
        self.configure(fg_color="white")
        self.transient(parent)
        self.grab_set()

        # Formulario
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text="Usuario:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0,5))
        self.entry_usuario = ctk.CTkEntry(frame, height=35)
        self.entry_usuario.pack(fill="x", pady=(0,15))

        ctk.CTkLabel(frame, text="Contraseña:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0,5))
        self.entry_password = ctk.CTkEntry(frame, show="*", height=35)
        self.entry_password.pack(fill="x", pady=(0,15))

        ctk.CTkLabel(frame, text="Rol:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0,5))
        self.combo_rol = ctk.CTkComboBox(frame, values=["Docente", "Administrativo"], height=35)
        self.combo_rol.set("Docente")
        self.combo_rol.pack(fill="x", pady=(0,20))

        btn_guardar = ctk.CTkButton(frame, text="Guardar Usuario", fg_color=COLOR_PRIMARY, command=self.guardar)
        btn_guardar.pack(fill="x", pady=5)

        btn_cancelar = ctk.CTkButton(frame, text="Cancelar", fg_color="transparent", text_color=COLOR_PRIMARY,
                                     border_width=1, border_color=COLOR_BORDER, command=self.destroy)
        btn_cancelar.pack(fill="x")

    def guardar(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        rol = self.combo_rol.get()
        if not usuario or not password:
            messagebox.showerror("Error", "Complete todos los campos.")
            return
        from data_base import guardar_usuario_db
        guardar_usuario_db(usuario, password, rol)
        messagebox.showinfo("Éxito", f"Usuario {usuario} creado.")
        if self.callback:
            self.callback()
        self.destroy()