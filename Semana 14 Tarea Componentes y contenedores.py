"""
Agenda Personal 
"""

import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, date


#  PALETA DE COLORES Y CONSTANTES DE ESTILO
BG_DARK      = "#1A1A2E"   # Fondo principal
BG_PANEL     = "#16213E"   # Fondo de paneles
BG_CARD      = "#0F3460"   # Tarjetas / secciones
ACCENT       = "#E94560"   # Rojo-rosa de acento
ACCENT_HOVER = "#FF6B6B"   # Acento hover
TEXT_PRIMARY = "#EAEAEA"   # Texto principal
TEXT_MUTED   = "#8892A4"   # Texto secundario
SUCCESS      = "#4ECDC4"   # Verde-azul para detalles
BORDER       = "#2A2A4A"   # Bordes sutiles

FONT_TITLE  = ("Courier New", 20, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")
FONT_BODY   = ("Courier New", 10)
FONT_SMALL  = ("Courier New",  9)
FONT_MONO   = ("Courier New", 10)


#  WIDGET: DatePicker  (calendario emergente)
class DatePicker(tk.Toplevel):
    """
    Ventana emergente con calendario interactivo para seleccionar una fecha.
    Se abre como ventana hija (Toplevel) y devuelve la fecha al campo Entry
    del formulario principal.
    """

    def __init__(self, parent, target_var: tk.StringVar):
        """
        parent     : widget padre (ventana principal)
        target_var : StringVar donde se escribirá la fecha seleccionada
        """
        super().__init__(parent)
        self.target_var = target_var
        self.title("Seleccionar Fecha")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.grab_set()          # Modal: bloquea la ventana padre

        today = date.today()
        self.year  = today.year
        self.month = today.month

        self._build_ui()
        self._center_on_parent(parent)

    
    # Posicionar en el centro de la ventana padre

    def _center_on_parent(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width()  // 2 - self.winfo_width()  // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{px}+{py}")

    
    # Construir toda la UI del calendario

    def _build_ui(self):
        # Cabecera con año/mes y botones de navegación
        header = tk.Frame(self, bg=BG_CARD, pady=8)
        header.pack(fill="x")

        btn_style = dict(bg=BG_CARD, fg=ACCENT, font=FONT_HEAD,
                         bd=0, cursor="hand2", activebackground=BG_CARD,
                         activeforeground=ACCENT_HOVER)

        tk.Button(header, text="◀", command=self._prev_month, **btn_style).pack(side="left",  padx=10)
        tk.Button(header, text="▶", command=self._next_month, **btn_style).pack(side="right", padx=10)

        self.header_lbl = tk.Label(header, bg=BG_CARD, fg=TEXT_PRIMARY, font=FONT_HEAD)
        self.header_lbl.pack(side="left", expand=True)

        # Nombres de días de la semana
        days_frame = tk.Frame(self, bg=BG_PANEL, pady=4)
        days_frame.pack(fill="x")
        for i, d in enumerate(["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]):
            color = ACCENT if d in ("Sá", "Do") else TEXT_MUTED
            tk.Label(days_frame, text=d, bg=BG_PANEL, fg=color,
                     font=FONT_SMALL, width=4).grid(row=0, column=i, padx=2)

        # Grid de días (se rellena dinámicamente)
        self.grid_frame = tk.Frame(self, bg=BG_DARK, padx=8, pady=8)
        self.grid_frame.pack()

        # Botón "Hoy"
        tk.Button(self, text="Hoy", command=self._select_today,
                  bg=ACCENT, fg="white", font=FONT_SMALL, bd=0,
                  pady=6, cursor="hand2",
                  activebackground=ACCENT_HOVER, activeforeground="white"
                  ).pack(fill="x", padx=12, pady=(0, 10))

        self._render_calendar()

    
    # Renderizar el mes actual

    def _render_calendar(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        self.header_lbl.config(
            text=f"{calendar.month_name[self.month].upper()}  {self.year}"
        )

        today = date.today()
        cal   = calendar.monthcalendar(self.year, self.month)

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(self.grid_frame, text="", bg=BG_DARK, width=4).grid(row=r, column=c)
                    continue

                is_today   = (day == today.day and self.month == today.month and self.year == today.year)
                is_weekend = c >= 5

                bg  = ACCENT         if is_today   else BG_DARK
                fg  = "white"        if is_today   else (ACCENT if is_weekend else TEXT_PRIMARY)
                fnt = ("Courier New", 10, "bold") if is_today else FONT_BODY

                btn = tk.Button(
                    self.grid_frame,
                    text=str(day),
                    width=3,
                    bg=bg, fg=fg,
                    font=fnt,
                    bd=0,
                    cursor="hand2",
                    relief="flat",
                    activebackground=BG_CARD,
                    activeforeground=ACCENT_HOVER,
                    command=lambda d=day: self._select_day(d)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)

    
    # Seleccionar un día

    def _select_day(self, day: int):
        fecha = date(self.year, self.month, day)
        self.target_var.set(fecha.strftime("%d/%m/%Y"))
        self.destroy()

    def _select_today(self):
        hoy = date.today()
        self.year, self.month = hoy.year, hoy.month
        self._select_day(hoy.day)

    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._render_calendar()

    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._render_calendar()


#  APLICACIÓN PRINCIPAL: AgendaApp
class AgendaApp(tk.Tk):
    """
    Ventana principal de la Agenda Personal.
    Organizada en tres frames:
      • frame_lista   → TreeView de eventos
      • frame_form    → Formulario de entrada
      • frame_actions → Botones de acción
    """

    def __init__(self):
        super().__init__()
        self.title("Agenda Personal")
        self.geometry("860x620")
        self.minsize(760, 540)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Variables del formulario
        self.var_fecha = tk.StringVar()
        self.var_hora  = tk.StringVar(value="09:00")
        self.var_desc  = tk.StringVar()
        self.var_cat   = tk.StringVar(value="Personal")

        self._build_ui()
        self._load_sample_data()


    #  CONSTRUCCIÓN DE LA UI

    def _build_ui(self):
        self._build_header()

        # Contenedor principal: lista (izq) + formulario (der)
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        self._build_list_frame(main)
        self._build_form_frame(main)

    
    # Cabecera 
    def _build_header(self):
        header = tk.Frame(self, bg=BG_CARD, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Franja de acento izquierda
        tk.Frame(header, bg=ACCENT, width=5).pack(side="left", fill="y")

        tk.Label(
            header,
            text="◈  AGENDA PERSONAL",
            bg=BG_CARD, fg=TEXT_PRIMARY,
            font=FONT_TITLE, padx=16
        ).pack(side="left", pady=12)

        # Fecha y hora en tiempo real (esquina derecha)
        self.clock_lbl = tk.Label(header, bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL)
        self.clock_lbl.pack(side="right", padx=16)
        self._tick()

    
    # Reloj en tiempo real
    
    def _tick(self):
        now = datetime.now().strftime("%A, %d %b %Y  |  %H:%M:%S")
        self.clock_lbl.config(text=now.upper())
        self.after(1000, self._tick)

    
    # Frame izquierdo: TreeView
    
    def _build_list_frame(self, parent):
        frame = tk.Frame(parent, bg=BG_PANEL, bd=0)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Título del panel
        tk.Label(frame, text="EVENTOS PROGRAMADOS",
                 bg=BG_PANEL, fg=ACCENT, font=FONT_HEAD,
                 pady=10, padx=12, anchor="w").pack(fill="x")

        tk.Frame(frame, bg=ACCENT, height=1).pack(fill="x")

        
        # TreeView
    
        columns = ("fecha", "hora", "categoria", "descripcion")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Agenda.Treeview",
                        background=BG_PANEL, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_PANEL, rowheight=30,
                        font=FONT_BODY, borderwidth=0)
        style.configure("Agenda.Treeview.Heading",
                        background=BG_CARD, foreground=SUCCESS,
                        font=FONT_HEAD, relief="flat", borderwidth=0)
        style.map("Agenda.Treeview",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT)])

        tree_container = tk.Frame(frame, bg=BG_PANEL)
        tree_container.pack(fill="both", expand=True, padx=8, pady=8)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Agenda.Treeview",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.config(command=self.tree.yview)

        # Configurar columnas
        col_cfg = [
            ("fecha",       "FECHA",       90,  "center"),
            ("hora",        "HORA",        65,  "center"),
            ("categoria",   "CATEGORÍA",   100, "center"),
            ("descripcion", "DESCRIPCIÓN", 260, "w"),
        ]
        for col, heading, width, anchor in col_cfg:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor, minwidth=40)

        self.tree.pack(fill="both", expand=True)

        # Tags de color por categoría
        self.tree.tag_configure("Personal",  foreground="#A8DADC")
        self.tree.tag_configure("Trabajo",   foreground="#FFD166")
        self.tree.tag_configure("Salud",     foreground="#06D6A0")
        self.tree.tag_configure("Estudio",   foreground="#EF8354")
        self.tree.tag_configure("Otro",      foreground=TEXT_PRIMARY)

        # Contador de eventos
        self.count_lbl = tk.Label(frame, bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_SMALL, pady=4)
        self.count_lbl.pack()

    
    # Frame derecho: Formulario
    
    def _build_form_frame(self, parent):
        frame = tk.Frame(parent, bg=BG_PANEL)
        frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(frame, text="NUEVO EVENTO",
                 bg=BG_PANEL, fg=ACCENT, font=FONT_HEAD,
                 pady=10, padx=12, anchor="w").pack(fill="x")
        tk.Frame(frame, bg=ACCENT, height=1).pack(fill="x")

        inner = tk.Frame(frame, bg=BG_PANEL, padx=16, pady=12)
        inner.pack(fill="both", expand=True)

        
        # Campo: Fecha
    
        self._label(inner, "FECHA *")
        fecha_row = tk.Frame(inner, bg=BG_PANEL)
        fecha_row.pack(fill="x", pady=(0, 10))

        self.entry_fecha = self._entry(fecha_row, self.var_fecha, "DD/MM/AAAA")
        self.entry_fecha.pack(side="left", fill="x", expand=True)

        tk.Button(
            fecha_row, text="📅",
            command=self._open_datepicker,
            bg=BG_CARD, fg=ACCENT, font=("Segoe UI Emoji", 12),
            bd=0, cursor="hand2", padx=8,
            activebackground=BORDER, activeforeground=ACCENT_HOVER
        ).pack(side="left", padx=(6, 0))

        
        # Campo: Hora
    
        self._label(inner, "HORA *  (HH:MM)")
        self.entry_hora = self._entry(inner, self.var_hora)
        self.entry_hora.pack(fill="x", pady=(0, 10))

        
        # Campo: Categoría
    
        self._label(inner, "CATEGORÍA")
        cat_frame = tk.Frame(inner, bg=BG_PANEL)
        cat_frame.pack(fill="x", pady=(0, 10))
        categorias = ["Personal", "Trabajo", "Salud", "Estudio", "Otro"]
        for cat in categorias:
            tk.Radiobutton(
                cat_frame, text=cat, variable=self.var_cat, value=cat,
                bg=BG_PANEL, fg=TEXT_MUTED, selectcolor=BG_CARD,
                activebackground=BG_PANEL, activeforeground=ACCENT,
                font=FONT_SMALL, cursor="hand2"
            ).pack(side="left", padx=(0, 8))

        
        # Campo: Descripción
    
        self._label(inner, "DESCRIPCIÓN *")
        desc_frame = tk.Frame(inner, bg=BG_CARD, bd=1, relief="flat")
        desc_frame.pack(fill="x", pady=(0, 14))
        self.text_desc = tk.Text(
            desc_frame, height=4, bg=BG_CARD, fg=TEXT_PRIMARY,
            font=FONT_MONO, insertbackground=ACCENT,
            relief="flat", padx=8, pady=6, wrap="word",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER
        )
        self.text_desc.pack(fill="x")

        
        # Botones
    
        self._build_buttons(inner)

    
    # Botones de acción 
    def _build_buttons(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(4, 12))

        btn_add = tk.Button(
            parent,
            text="  ＋  AGREGAR EVENTO",
            command=self.agregar_evento,
            bg=ACCENT, fg="white", font=FONT_HEAD,
            bd=0, pady=9, cursor="hand2",
            activebackground=ACCENT_HOVER, activeforeground="white"
        )
        btn_add.pack(fill="x", pady=(0, 8))

        btn_del = tk.Button(
            parent,
            text="  ✕  ELIMINAR SELECCIONADO",
            command=self.eliminar_evento,
            bg=BG_CARD, fg=ACCENT, font=FONT_HEAD,
            bd=1, pady=9, cursor="hand2",
            activebackground=BORDER, activeforeground=ACCENT_HOVER,
            relief="flat", highlightthickness=1, highlightbackground=ACCENT
        )
        btn_del.pack(fill="x", pady=(0, 8))

        tk.Button(
            parent,
            text="LIMPIAR FORMULARIO",
            command=self.limpiar_formulario,
            bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_SMALL,
            bd=0, pady=6, cursor="hand2",
            activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY
        ).pack(fill="x", pady=(0, 8))

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(4, 12))

        tk.Button(
            parent,
            text="SALIR",
            command=self._confirmar_salir,
            bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_SMALL,
            bd=0, pady=6, cursor="hand2",
            activebackground=BG_PANEL, activeforeground=ACCENT
        ).pack(fill="x")


    #  UTILIDADES DE UI

    def _label(self, parent, text: str):
        tk.Label(parent, text=text, bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(0, 2))

    def _entry(self, parent, textvariable=None, placeholder=""):
        e = tk.Entry(
            parent,
            textvariable=textvariable,
            bg=BG_CARD, fg=TEXT_PRIMARY, font=FONT_MONO,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER, bd=0
        )
        e.config({"disabledbackground": BG_CARD})

        # Placeholder ligero (color gris mientras vacío)
        if placeholder and textvariable:
            def on_focus_in(event, e=e, ph=placeholder, var=textvariable):
                if var.get() == ph:
                    var.set("")
                    e.config(fg=TEXT_PRIMARY)

            def on_focus_out(event, e=e, ph=placeholder, var=textvariable):
                if not var.get():
                    var.set(ph)
                    e.config(fg=TEXT_MUTED)

            if not textvariable.get():
                textvariable.set(placeholder)
                e.config(fg=TEXT_MUTED)

            e.bind("<FocusIn>",  on_focus_in)
            e.bind("<FocusOut>", on_focus_out)

        return e


    #  ACCIONES PRINCIPALES

    def _open_datepicker(self):
        """Abre el calendario emergente y vincula la fecha seleccionada al campo."""
        DatePicker(self, self.var_fecha)

    def agregar_evento(self):
        """
        Valida los campos del formulario y agrega un nuevo evento al TreeView.
        Muestra un mensaje de error si faltan datos o el formato es incorrecto.
        """
        fecha = self.var_fecha.get().strip()
        hora  = self.var_hora.get().strip()
        cat   = self.var_cat.get().strip()
        desc  = self.text_desc.get("1.0", "end-1c").strip()

        
        # Validaciones
    
        errores = []
        if not fecha or fecha == "DD/MM/AAAA":
            errores.append("• La fecha es obligatoria.")
        else:
            try:
                datetime.strptime(fecha, "%d/%m/%Y")
            except ValueError:
                errores.append("• Formato de fecha inválido. Use DD/MM/AAAA.")

        if not hora:
            errores.append("• La hora es obligatoria.")
        else:
            try:
                datetime.strptime(hora, "%H:%M")
            except ValueError:
                errores.append("• Formato de hora inválido. Use HH:MM.")

        if not desc:
            errores.append("• La descripción es obligatoria.")

        if errores:
            messagebox.showerror("Datos incompletos", "\n".join(errores), parent=self)
            return

        
        # Insertar en el TreeView
    
        self.tree.insert(
            "", "end",
            values=(fecha, hora, cat, desc),
            tags=(cat,)
        )
        self._actualizar_contador()
        self.limpiar_formulario()

        # Ordenar automáticamente por fecha y hora
        self._ordenar_eventos()

    def eliminar_evento(self):
        """
        Elimina el evento seleccionado en el TreeView, previa confirmación
        mediante un diálogo de confirmación.
        """
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Sin selección",
                "Seleccione un evento en la lista para eliminarlo.",
                parent=self
            )
            return

        item  = seleccion[0]
        vals  = self.tree.item(item, "values")
        resumen = f"  {vals[0]}  {vals[1]}  |  {vals[3][:40]}{'...' if len(vals[3]) > 40 else ''}"

        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar este evento?\n\n{resumen}",
            icon="warning",
            parent=self
        )
        if confirmado:
            self.tree.delete(item)
            self._actualizar_contador()

    def limpiar_formulario(self):
        """Restablece todos los campos del formulario a sus valores iniciales."""
        self.var_fecha.set("DD/MM/AAAA")
        self.entry_fecha.config(fg=TEXT_MUTED)
        self.var_hora.set("09:00")
        self.var_cat.set("Personal")
        self.text_desc.delete("1.0", "end")

    def _ordenar_eventos(self):
        """Ordena los eventos del TreeView por fecha y hora ascendentes."""
        items = [(self.tree.set(k, "fecha") + self.tree.set(k, "hora"), k)
                 for k in self.tree.get_children("")]
        # Convertir "DD/MM/AAAA" a "AAAA/MM/DD" para ordenar correctamente
        def sort_key(pair):
            try:
                d = datetime.strptime(pair[0][:10], "%d/%m/%Y")
                return d.strftime("%Y%m%d") + pair[0][10:]
            except ValueError:
                return pair[0]

        items.sort(key=sort_key)
        for i, (_, k) in enumerate(items):
            self.tree.move(k, "", i)

    def _actualizar_contador(self):
        """Actualiza la etiqueta con el total de eventos en la lista."""
        n = len(self.tree.get_children())
        plural = "evento" if n == 1 else "eventos"
        self.count_lbl.config(text=f"{n} {plural} registrados")

    def _confirmar_salir(self):
        """Muestra un diálogo de confirmación antes de cerrar la aplicación."""
        if messagebox.askyesno("Salir", "¿Cerrar la Agenda Personal?", parent=self):
            self.destroy()


    #  DATOS DE EJEMPLO

    def _load_sample_data(self):
        """Inserta algunos eventos de ejemplo para demostrar la interfaz."""
        ejemplos = [
            ("22/03/2026", "09:00", "Trabajo",   "Reunión de equipo — revisión de sprints"),
            ("22/03/2026", "13:00", "Salud",     "Cita médica de chequeo anual"),
            ("23/03/2026", "10:30", "Estudio",   "Clase de Python avanzado"),
            ("25/03/2026", "19:00", "Personal",  "Cena familiar — cumpleaños de mamá"),
            ("28/03/2026", "08:00", "Trabajo",   "Entrega del informe Q1 al cliente"),
            ("30/03/2026", "11:00", "Estudio",   "Examen final de estructuras de datos"),
        ]
        for fecha, hora, cat, desc in ejemplos:
            self.tree.insert("", "end", values=(fecha, hora, cat, desc), tags=(cat,))
        self._actualizar_contador()


#  PUNTO DE ENTRADA
if __name__ == "__main__":
    app = AgendaApp()
    app.mainloop()