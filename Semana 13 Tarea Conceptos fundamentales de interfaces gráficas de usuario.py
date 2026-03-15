
# GESTOR DE DATOS — Aplicación GUI con Tkinter
# Descripción : Aplicación de escritorio para agregar, visualizar
#               filtrar y eliminar registros de forma visual.
# Librería GUI : tkinter 

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime

# PALETA DE COLORES 
BG        = "#0e0f11"   # Fondo principal
SURFACE   = "#16181c"   # Superficie de cards/panels
SURFACE2  = "#1e2127"   # Superficie secundaria (
BORDER    = "#2a2d35"   # Bordes
ACCENT    = "#f0c040"   
ACCENT2   = "#3b82f6"   
DANGER    = "#ef4444"   # Rojo para eliminar / errores
SUCCESS   = "#22c55e"   # Verde para éxito
TEXT      = "#e8eaf0"   # Texto principal
TEXT_MUTED= "#7a7f8e"   # Texto secundario 

# CLASE PRINCIPAL DE LA APLICACIÓN
class GestorDatosApp:
    """
    Clase principal que construye y gestiona toda la interfaz gráfica.
    Separa la UI (build_*) de la lógica (agregar, eliminar, filtrar…).
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configurar_ventana()

        # Variables de control vinculadas a los widgets del formulario
        self.var_nombre    = tk.StringVar()
        self.var_email     = tk.StringVar()
        self.var_categoria = tk.StringVar(value="Personal")
        self.var_prioridad = tk.StringVar(value="Media")
        self.var_buscar    = tk.StringVar()
        self.var_buscar.trace_add("write", lambda *_: self._filtrar())

        # Contador para IDs únicos
        self._id_counter = 1

        # Lista maestra de registros: cada elemento es un dict
        self.datos: list[dict] = []

        # ID del registro actualmente seleccionado en la tabla
        self.seleccionado_id: int | None = None

        # Estado del toast (Label flotante)
        self._toast_after = None

        # Construir la interfaz
        self._build_ui()

        # Insertar datos de ejemplo para demostración
        self._cargar_ejemplos()

    # CONFIGURACIÓN DE LA VENTANA PRINCIPAL
    def _configurar_ventana(self):
        """Ajusta título, tamaño, color de fondo y centrado."""
        self.root.title("Gestor de Datos — Aplicación GUI")
        self.root.geometry("1100x680")
        self.root.minsize(800, 520)
        self.root.configure(bg=BG)
        # Centrar en pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 1100) // 2
        y = (self.root.winfo_screenheight() -  680) // 2
        self.root.geometry(f"+{x}+{y}")

    # BUILD INTERFAZ COMPLETA
    def _build_ui(self):
        """Construye todos los paneles de la interfaz."""
        self._build_header()

        # Contenedor horizontal: formulario + tabla 
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        main.columnconfigure(0, minsize=320)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_form_panel(main)
        self._build_table_panel(main)
        self._build_stats_bar()
        self._build_toast()

    #  Encabezado
    def _build_header(self):
        """Título y subtítulo de la aplicación."""
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 12))

        eyebrow = tk.Label(
            header,
            text="APLICACIÓN GUI · TKINTER PYTHON",
            bg=BG, fg=ACCENT,
            font=("Courier", 8, "bold")
        )
        eyebrow.pack(anchor="w")

        title = tk.Label(
            header,
            text="Gestor de Datos",
            bg=BG, fg=TEXT,
            font=("Courier", 22, "bold")
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Agrega, filtra y administra registros de forma visual e intuitiva.",
            bg=BG, fg=TEXT_MUTED,
            font=("Courier", 9)
        )
        subtitle.pack(anchor="w")

        # Línea divisoria
        sep = tk.Frame(self.root, height=1, bg=BORDER)
        sep.pack(fill="x", padx=24, pady=(8, 0))

    #  Panel Izquierdo: Formulario ─
    def _build_form_panel(self, parent):
        """
        Panel con todos los campos de entrada:
        Nombre, Email, Categoría, Prioridad, Notas
        y los botones Agregar / Limpiar / Eliminar seleccionado.
        """
        frame = tk.Frame(parent, bg=SURFACE, bd=0, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=8)
        frame.columnconfigure(0, weight=1)

        # Título del panel
        self._section_title(frame, "NUEVO REGISTRO").pack(
            fill="x", padx=16, pady=(14, 6))

        pad = {"padx": 16, "pady": 4}

        #  Nombre 
        self._label(frame, "Nombre *").pack(anchor="w", **pad)
        self.entry_nombre = self._entry(frame, self.var_nombre,
                                        placeholder="Ej. Juan Pérez")
        self.entry_nombre.pack(fill="x", **pad)
        self.entry_nombre.bind("<Return>", lambda _: self.agregar())

        #  Email 
        self._label(frame, "Correo electrónico").pack(anchor="w", **pad)
        self.entry_email = self._entry(frame, self.var_email,
                                       placeholder="correo@ejemplo.com")
        self.entry_email.pack(fill="x", **pad)

        #  Categoría + Prioridad en fila 
        row2 = tk.Frame(frame, bg=SURFACE)
        row2.pack(fill="x", **pad)
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)

        cat_frame = tk.Frame(row2, bg=SURFACE)
        cat_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._label(cat_frame, "Categoría").pack(anchor="w")
        self.combo_cat = self._combobox(
            cat_frame, self.var_categoria,
            ["Personal", "Trabajo", "Estudio", "Otro"]
        )
        self.combo_cat.pack(fill="x")

        prio_frame = tk.Frame(row2, bg=SURFACE)
        prio_frame.grid(row=0, column=1, sticky="ew")
        self._label(prio_frame, "Prioridad").pack(anchor="w")
        self.combo_prio = self._combobox(
            prio_frame, self.var_prioridad,
            ["Alta", "Media", "Baja"]
        )
        self.combo_prio.pack(fill="x")

        #  Notas 
        self._label(frame, "Notas").pack(anchor="w", **pad)
        self.text_notas = tk.Text(
            frame,
            height=5,
            bg=SURFACE2, fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Courier", 10),
            bd=0,
            highlightbackground=BORDER,
            highlightthickness=1,
            wrap="word"
        )
        self.text_notas.pack(fill="x", **pad)

        # Contador de caracteres para el textarea
        self.lbl_chars = tk.Label(frame, text="0 / 200",
                                  bg=SURFACE, fg=TEXT_MUTED,
                                  font=("Courier", 8))
        self.lbl_chars.pack(anchor="e", padx=16)
        self.text_notas.bind("<KeyRelease>", self._actualizar_contador)

        # Separador
        tk.Frame(frame, height=1, bg=BORDER).pack(fill="x", padx=16, pady=8)

        #  Botones principales 
        btn_row = tk.Frame(frame, bg=SURFACE)
        btn_row.pack(fill="x", padx=16, pady=(0, 6))
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, minsize=80)

        self._btn_primary(btn_row, "＋  Agregar", self.agregar).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        self._btn_ghost(btn_row, "✕  Limpiar", self.limpiar).grid(
            row=0, column=1, sticky="ew")

        #  Botón eliminar seleccionado 
        self._btn_danger(
            frame,
            "🗑  Eliminar registro seleccionado",
            self.eliminar_seleccionado
        ).pack(fill="x", padx=16, pady=(4, 16))

    #  Panel Derecho: Tabla 
    def _build_table_panel(self, parent):
        """
        Panel con buscador y tabla (Treeview) que muestra
        todos los registros. Soporta selección y ordenamiento.
        """
        frame = tk.Frame(parent, bg=SURFACE, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
        frame.grid(row=0, column=1, sticky="nsew", pady=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        #  Barra superior (título + buscador + badge) 
        top = tk.Frame(frame, bg=SURFACE)
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        top.columnconfigure(1, weight=1)

        self._section_title(top, "REGISTROS GUARDADOS").grid(
            row=0, column=0, sticky="w")

        self.entry_buscar = self._entry(top, self.var_buscar,
                                        placeholder="🔍  Buscar…")
        self.entry_buscar.grid(row=0, column=1, sticky="ew", padx=(12, 8))

        self.lbl_badge = tk.Label(
            top, text="0 registros",
            bg=SURFACE2, fg=TEXT_MUTED,
            font=("Courier", 8),
            padx=10, pady=4,
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1
        )
        self.lbl_badge.grid(row=0, column=2, sticky="e")

        #  Treeview (tabla) 
        cols = ("nombre", "email", "categoria", "prioridad", "notas", "fecha")
        self.tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            selectmode="browse"
        )

        # Estilo del Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                         background=SURFACE2,
                         foreground=TEXT,
                         rowheight=32,
                         fieldbackground=SURFACE2,
                         font=("Courier", 9),
                         borderwidth=0)
        style.configure("Treeview.Heading",
                         background=SURFACE,
                         foreground=TEXT_MUTED,
                         font=("Courier", 8, "bold"),
                         relief="flat",
                         borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#0e0f11")])
        style.map("Treeview.Heading",
                  background=[("active", SURFACE2)])

        # Configurar columnas y encabezados
        col_config = {
            "nombre":    ("Nombre",     180, True),
            "email":     ("Correo",     180, True),
            "categoria": ("Categoría",   90, True),
            "prioridad": ("Prioridad",   80, True),
            "notas":     ("Notas",      160, False),
            "fecha":     ("Fecha",       80, False),
        }
        for col, (header, width, sortable) in col_config.items():
            cmd = (lambda c=col: self._sort_by(c)) if sortable else None
            self.tree.heading(col, text=header, command=cmd)
            self.tree.column(col, width=width, minwidth=60, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0,0))
        vsb.grid(row=1, column=1, sticky="ns",  pady=(0, 0))
        hsb.grid(row=2, column=0, sticky="ew",  padx=(16, 0), pady=(0, 16))
        frame.rowconfigure(1, weight=1)

        # Evento de selección de fila
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Alternar colores de filas pares/impares
        self.tree.tag_configure("odd",  background=SURFACE2)
        self.tree.tag_configure("even", background="#191b20")

    #  Barra de estadísticas 
    def _build_stats_bar(self):
        """4 tarjetas con métricas actualizadas en tiempo real."""
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=24, pady=(0, 16))
        for i in range(4):
            bar.columnconfigure(i, weight=1)

        stats = [
            ("stat_total", "TOTAL REGISTROS"),
            ("stat_alta",  "PRIORIDAD ALTA"),
            ("stat_cat",   "CATEGORÍA MÁS USADA"),
            ("stat_last",  "ÚLTIMO AGREGADO"),
        ]
        self.stat_labels = {}

        for col, (key, title) in enumerate(stats):
            card = tk.Frame(bar, bg=SURFACE,
                            highlightbackground=BORDER,
                            highlightthickness=1)
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 8, 0))

            tk.Label(card, text=title, bg=SURFACE, fg=TEXT_MUTED,
                     font=("Courier", 7, "bold")).pack(anchor="w", padx=12, pady=(10, 0))

            lbl = tk.Label(card, text="0", bg=SURFACE, fg=ACCENT,
                           font=("Courier", 18, "bold"))
            lbl.pack(anchor="w", padx=12, pady=(2, 10))
            self.stat_labels[key] = lbl

    #  Toast de notificaciones 
    def _build_toast(self):
        """Label flotante en la esquina inferior derecha para feedback."""
        self.toast = tk.Label(
            self.root,
            text="",
            bg=SUCCESS, fg="white",
            font=("Courier", 9, "bold"),
            padx=16, pady=8,
            relief="flat"
        )
        # No se coloca con pack/grid; se posiciona con place() al mostrarse

    # WIDGETS HELPERS (fábrica de componentes estilizados)
    def _label(self, parent, text):
        return tk.Label(parent, text=text, bg=parent.cget("bg"),
                        fg=TEXT_MUTED, font=("Courier", 8, "bold"))

    def _section_title(self, parent, text):
        f = tk.Frame(parent, bg=parent.cget("bg"))
        tk.Frame(f, width=8, height=8, bg=ACCENT).pack(side="left", padx=(0, 6))
        tk.Label(f, text=text, bg=parent.cget("bg"), fg=TEXT_MUTED,
                 font=("Courier", 8, "bold")).pack(side="left")
        return f

    def _entry(self, parent, textvariable, placeholder=""):
        """Entry estilizado con color de fondo oscuro."""
        e = tk.Entry(
            parent,
            textvariable=textvariable,
            bg=SURFACE2, fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=("Courier", 10),
            bd=0,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        e.config({"width": 1})  # Permite que se expanda con fill="x"
        # Placeholder simulado
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=TEXT_MUTED)

            def on_focus_in(event, en=e, ph=placeholder):
                if en.get() == ph:
                    en.delete(0, "end")
                    en.config(fg=TEXT)

            def on_focus_out(event, en=e, ph=placeholder, tv=textvariable):
                if not en.get():
                    en.insert(0, ph)
                    en.config(fg=TEXT_MUTED)

            e.bind("<FocusIn>",  on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
            # No vincular la variable si está mostrando placeholder
            textvariable.set("")

        # Efectos focus
        e.bind("<FocusIn>",  lambda ev: e.config(highlightbackground=ACCENT),   add="+")
        e.bind("<FocusOut>", lambda ev: e.config(highlightbackground=BORDER),   add="+")
        return e

    def _combobox(self, parent, variable, values):
        """Combobox readonly estilizado."""
        style = ttk.Style()
        style.configure("Dark.TCombobox",
                         fieldbackground=SURFACE2,
                         background=SURFACE2,
                         foreground=TEXT,
                         arrowcolor=ACCENT,
                         selectbackground=SURFACE2,
                         selectforeground=TEXT)
        cb = ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            state="readonly",
            font=("Courier", 10),
            style="Dark.TCombobox"
        )
        return cb

    def _btn_primary(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=ACCENT, fg="#0e0f11",
            font=("Courier", 9, "bold"),
            relief="flat", cursor="hand2",
            activebackground="#d4a820",
            activeforeground="#0e0f11",
            pady=7
        )

    def _btn_ghost(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=SURFACE2, fg=TEXT_MUTED,
            font=("Courier", 9),
            relief="flat", cursor="hand2",
            activebackground=BORDER,
            activeforeground=TEXT,
            pady=7,
            highlightbackground=BORDER,
            highlightthickness=1
        )

    def _btn_danger(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=SURFACE, fg=DANGER,
            font=("Courier", 9),
            relief="flat", cursor="hand2",
            activebackground="#2a1010",
            activeforeground=DANGER,
            pady=7,
            highlightbackground="#4a1515",
            highlightthickness=1
        )

    # LÓGICA DE NEGOCIO

    def agregar(self):
        """
        Valida los campos del formulario y, si son correctos,
        crea un nuevo registro y lo agrega a la tabla.
        """
        nombre    = self.var_nombre.get().strip()
        email     = self.var_email.get().strip()
        categoria = self.var_categoria.get()
        prioridad = self.var_prioridad.get()
        notas     = self.text_notas.get("1.0", "end-1c").strip()

        # Validación
        if not nombre:
            messagebox.showwarning("Campo requerido",
                                   "El campo 'Nombre' es obligatorio.",
                                   parent=self.root)
            self.entry_nombre.focus()
            return

        if email and "@" not in email:
            messagebox.showwarning("Email inválido",
                                   "El correo electrónico no tiene un formato válido.",
                                   parent=self.root)
            self.entry_email.focus()
            return

        if len(notas) > 200:
            messagebox.showwarning("Notas muy largas",
                                   "Las notas no pueden superar 200 caracteres.",
                                   parent=self.root)
            return

        # Crear registro
        registro = {
            "id":        self._id_counter,
            "nombre":    nombre,
            "email":     email or "—",
            "categoria": categoria,
            "prioridad": prioridad,
            "notas":     notas or "—",
            "fecha":     datetime.now().strftime("%d/%m/%Y"),
        }
        self._id_counter += 1
        self.datos.append(registro)

        # Actualizar UI
        self._render_tabla()
        self._actualizar_estadisticas()
        self.limpiar(show_toast=False)
        self._mostrar_toast(f'Registro "{nombre}" agregado.', kind="success")

    def limpiar(self, show_toast=True):
        """
        Borra todos los campos del formulario y restablece
        los selectores a sus valores predeterminados.
        """
        self.var_nombre.set("")
        self.var_email.set("")
        self.var_categoria.set("Personal")
        self.var_prioridad.set("Media")
        self.text_notas.delete("1.0", "end")
        self.lbl_chars.config(text="0 / 200", fg=TEXT_MUTED)

        # Limpiar placeholders visualmente
        for entry, ph in [(self.entry_nombre, "Ej. Juan Pérez"),
                          (self.entry_email,  "correo@ejemplo.com")]:
            entry.delete(0, "end")
            entry.insert(0, ph)
            entry.config(fg=TEXT_MUTED)

        if show_toast:
            self._mostrar_toast("Formulario limpiado.", kind="info")

    def eliminar_seleccionado(self):
        """
        Elimina el registro actualmente seleccionado en la tabla.
        Muestra un cuadro de confirmación antes de proceder.
        """
        if self.seleccionado_id is None:
            messagebox.showinfo("Sin selección",
                                "Haz clic en un registro de la tabla primero.",
                                parent=self.root)
            return

        reg = next((r for r in self.datos if r["id"] == self.seleccionado_id), None)
        if reg is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el registro de «{reg['nombre']}»?",
            parent=self.root
        )
        if not confirmar:
            return

        nombre = reg["nombre"]
        self.datos = [r for r in self.datos if r["id"] != self.seleccionado_id]
        self.seleccionado_id = None

        self._render_tabla()
        self._actualizar_estadisticas()
        self._mostrar_toast(f'Registro "{nombre}" eliminado.', kind="info")

    # RENDERIZADO DE LA TABLA

    def _render_tabla(self, filtro=""):
        """
        Limpia y repopula el Treeview con los registros de `self.datos`,
        aplicando el filtro de búsqueda si se proporciona.
        """
        # Guardar IID seleccionado para restaurarlo si sigue visible
        prev_sel = self.seleccionado_id

        # Borrar filas actuales
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # Filtrar registros
        q = filtro.lower()
        filtrados = [
            r for r in self.datos
            if q in (r["nombre"] + r["email"] + r["categoria"] +
                     r["prioridad"] + r["notas"]).lower()
        ] if q else list(self.datos)

        # Insertar filas con tag alternado
        for i, r in enumerate(filtrados):
            tag = "odd" if i % 2 == 0 else "even"
            iid = str(r["id"])
            self.tree.insert(
                "", "end", iid=iid, tags=(tag,),
                values=(
                    r["nombre"],
                    r["email"],
                    r["categoria"],
                    r["prioridad"],
                    r["notas"],
                    r["fecha"],
                )
            )
            # Restaurar selección si la fila sigue presente
            if r["id"] == prev_sel:
                self.tree.selection_set(iid)
                self.tree.focus(iid)

        # Actualizar badge
        n = len(filtrados)
        self.lbl_badge.config(
            text=f"{n} registro{'s' if n != 1 else ''}"
        )

    def _filtrar(self):
        """Llama a _render_tabla con el texto actual del buscador."""
        self._render_tabla(self.var_buscar.get())

    # ORDENAMIENTO DE COLUMNAS
    _sort_state: dict = {}  # {col: bool} True=ascendente

    def _sort_by(self, col):
        """Ordena self.datos por la clave dada y re-renderiza."""
        asc = not self._sort_state.get(col, False)
        self._sort_state[col] = asc
        self.datos.sort(key=lambda r: r[col].lower(), reverse=not asc)
        self._render_tabla(self.var_buscar.get())

        # Actualizar flechas en los encabezados
        arrows = {"nombre": "↕", "email": "↕", "categoria": "↕", "prioridad": "↕"}
        for c in arrows:
            if c == col:
                arrows[c] = "↑" if asc else "↓"
            self.tree.heading(c, text=c.capitalize() + " " + arrows[c])

    # ESTADÍSTICAS
    def _actualizar_estadisticas(self):
        """Recalcula y actualiza las 4 tarjetas de métricas."""
        total = len(self.datos)
        alta  = sum(1 for r in self.datos if r["prioridad"] == "Alta")

        # Categoría más frecuente
        if self.datos:
            from collections import Counter
            cat_top = Counter(r["categoria"] for r in self.datos).most_common(1)[0][0]
        else:
            cat_top = "—"

        ultimo = self.datos[-1]["nombre"] if self.datos else "—"

        self.stat_labels["stat_total"].config(text=str(total))
        self.stat_labels["stat_alta"].config(text=str(alta))
        self.stat_labels["stat_cat"].config(text=cat_top,
                                            font=("Courier", 11, "bold"))
        self.stat_labels["stat_last"].config(text=ultimo,
                                             font=("Courier", 9, "bold"))

    # EVENTOS
    def _on_select(self, event):
        """Actualiza `seleccionado_id` cuando el usuario hace clic en una fila."""
        sel = self.tree.selection()
        self.seleccionado_id = int(sel[0]) if sel else None

    def _actualizar_contador(self, event=None):
        """Actualiza el contador de caracteres del textarea de Notas."""
        n = len(self.text_notas.get("1.0", "end-1c"))
        self.lbl_chars.config(
            text=f"{n} / 200",
            fg=DANGER if n > 160 else TEXT_MUTED
        )

    # TOAST (notificación temporal)
    def _mostrar_toast(self, mensaje, kind="info"):
        """
        Muestra un label temporal en la esquina inferior derecha.
        kind: 'success' | 'info' | 'error'
        """
        colores = {"success": SUCCESS, "info": ACCENT, "error": DANGER}
        fg_map  = {"success": "white",   "info": "#0e0f11", "error": "white"}

        self.toast.config(
            text=f"  {mensaje}  ",
            bg=colores.get(kind, ACCENT),
            fg=fg_map.get(kind, "#0e0f11")
        )
        self.toast.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        self.toast.lift()

        # Cancelar timer anterior si existe
        if self._toast_after:
            self.root.after_cancel(self._toast_after)

        # Ocultar automáticamente después de 2.8 segundos
        self._toast_after = self.root.after(2800, self.toast.place_forget)

    # DATOS DE EJEMPLO
    def _cargar_ejemplos(self):
        """Inserta 3 registros iniciales para demostración."""
        ejemplos = [
            ("Ana García",   "ana@ejemplo.com",   "Trabajo",  "Alta",  "Reunión el viernes"),
            ("Luis Moreno",  "luis@ejemplo.com",  "Estudio",  "Media", "Entregar tarea GUI"),
            ("María Torres", "maria@ejemplo.com", "Personal", "Baja",  "Llamar al médico"),
        ]
        for nombre, email, cat, prio, notas in ejemplos:
            self.datos.append({
                "id":        self._id_counter,
                "nombre":    nombre,
                "email":     email,
                "categoria": cat,
                "prioridad": prio,
                "notas":     notas,
                "fecha":     datetime.now().strftime("%d/%m/%Y"),
            })
            self._id_counter += 1

        self._render_tabla()
        self._actualizar_estadisticas()


# PUNTO DE ENTRADA
if __name__ == "__main__":
    root = tk.Tk()
    app = GestorDatosApp(root)
    root.mainloop()