"""
╔══════════════════════════════════════════════════════════╗
║         GESTIÓN DE TAREAS — Task Manager GUI             ║
║         Desarrollado con Tkinter                         ║
╚══════════════════════════════════════════════════════════╝

Atajos de teclado:
  Enter      → Añadir tarea
  C          → Marcar seleccionada como completada
  Delete / D → Eliminar tarea seleccionada
  Escape     → Cerrar aplicación
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import datetime


# Paleta de colores
COLORS = {
    "bg":           "#0F0F13",      # Fondo principal (casi negro)
    "surface":      "#1A1A24",      # Superficie de tarjetas
    "surface2":     "#22222E",      # Superficie secundaria
    "border":       "#2E2E42",      # Bordes sutiles
    "accent":       "#7C6AF7",      # Violeta-índigo (acento principal)
    "accent_hover": "#9B8FF9",      # Acento en hover
    "accent_dim":   "#3D3578",      # Acento oscuro / fondo botón
    "success":      "#3DDC84",      # Verde completado
    "success_dim":  "#1A4A32",      # Verde oscuro fondo
    "danger":       "#FF5C5C",      # Rojo eliminar
    "danger_dim":   "#4A1A1A",      # Rojo oscuro fondo
    "text":         "#E8E8F0",      # Texto principal
    "text_muted":   "#6B6B8A",      # Texto apagado
    "pending":      "#E8E8F0",      # Color tarea pendiente
    "done_fg":      "#3DDC84",      # Color tarea completada (texto)
    "done_bg":      "#131F19",      # Fondo tarea completada
    "selected_bg":  "#252540",      # Fondo ítem seleccionado
    "entry_bg":     "#16161F",      # Fondo campo de entrada
    "scrollbar":    "#2E2E42",
}

# Clase principal

class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gestión de Tareas")
        self.geometry("700x650")
        self.minsize(520, 480)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        # Centrar ventana
        self._center_window(700, 650)

        # Datos
        self.tasks: list[dict] = []          # {text, done, widget_id}

        # Fuentes
        self._setup_fonts()

        # UI
        self._build_ui()

        # Atajos globales
        self._bind_shortcuts()

        # Focus al campo de entrada
        self.entry.focus_set()

    # Utilidades

    def _center_window(self, w: int, h: int):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_fonts(self):
        self.font_title    = tkfont.Font(family="Courier", size=22, weight="bold")
        self.font_subtitle = tkfont.Font(family="Courier", size=10)
        self.font_entry    = tkfont.Font(family="Consolas", size=13)
        self.font_task     = tkfont.Font(family="Consolas", size=12)
        self.font_btn      = tkfont.Font(family="Courier", size=10, weight="bold")
        self.font_shortcut = tkfont.Font(family="Courier", size=9)
        self.font_counter  = tkfont.Font(family="Courier", size=10)
        self.font_empty    = tkfont.Font(family="Courier", size=12)
        self.font_tag      = tkfont.Font(family="Courier", size=8, weight="bold")

    # Construcción UI

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg"], pady=0)
        header.pack(fill="x", padx=24, pady=(20, 0))

        # Línea decorativa izquierda
        accent_bar = tk.Frame(header, bg=COLORS["accent"], width=4, height=52)
        accent_bar.pack(side="left", padx=(0, 12))

        title_frame = tk.Frame(header, bg=COLORS["bg"])
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="TASK MANAGER",
            font=self.font_title,
            fg=COLORS["text"],
            bg=COLORS["bg"],
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Gestión de tareas pendientes",
            font=self.font_subtitle,
            fg=COLORS["text_muted"],
            bg=COLORS["bg"],
        ).pack(anchor="w")

        # Contador derecha
        self.counter_var = tk.StringVar(value="0 tareas")
        tk.Label(
            header,
            textvariable=self.counter_var,
            font=self.font_counter,
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(side="right", anchor="ne", pady=4)

        # Separador
        self._separator(pady=(14, 16))

        # Campo de entrada
        input_outer = tk.Frame(self, bg=COLORS["border"], bd=0)
        input_outer.pack(fill="x", padx=24, pady=(0, 4))

        input_inner = tk.Frame(input_outer, bg=COLORS["entry_bg"], pady=2)
        input_inner.pack(fill="x", padx=1, pady=1)

        # Icono ➕
        tk.Label(
            input_inner,
            text="  ✦ ",
            font=self.font_entry,
            fg=COLORS["accent"],
            bg=COLORS["entry_bg"],
        ).pack(side="left")

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_inner,
            textvariable=self.entry_var,
            font=self.font_entry,
            fg=COLORS["text"],
            bg=COLORS["entry_bg"],
            insertbackground=COLORS["accent"],
            relief="flat",
            bd=0,
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=10)

        # Hint texto
        self.hint_label = tk.Label(
            input_inner,
            text="Enter ↵",
            font=self.font_shortcut,
            fg=COLORS["text_muted"],
            bg=COLORS["entry_bg"],
            padx=8,
        )
        self.hint_label.pack(side="right")

        # Barra de botones
        btn_frame = tk.Frame(self, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=24, pady=(10, 0))

        self.btn_add = self._make_button(
            btn_frame,
            text="＋  AÑADIR",
            shortcut="[Enter]",
            bg=COLORS["accent_dim"],
            fg=COLORS["accent_hover"],
            hover_bg="#4A3FA0",
            command=self.add_task,
        )
        self.btn_add.pack(side="left", padx=(0, 8))

        self.btn_complete = self._make_button(
            btn_frame,
            text="✔  COMPLETAR",
            shortcut="[C]",
            bg=COLORS["success_dim"],
            fg=COLORS["success"],
            hover_bg="#1F5C38",
            command=self.complete_task,
        )
        self.btn_complete.pack(side="left", padx=(0, 8))

        self.btn_delete = self._make_button(
            btn_frame,
            text="✕  ELIMINAR",
            shortcut="[Del/D]",
            bg=COLORS["danger_dim"],
            fg=COLORS["danger"],
            hover_bg="#6B2020",
            command=self.delete_task,
        )
        self.btn_delete.pack(side="left")

        # Botón limpiar completadas (derecha)
        self.btn_clear = self._make_button(
            btn_frame,
            text="⊘  LIMPIAR",
            shortcut="[completadas]",
            bg=COLORS["surface2"],
            fg=COLORS["text_muted"],
            hover_bg=COLORS["border"],
            command=self.clear_completed,
        )
        self.btn_clear.pack(side="right")

        # Separador
        self._separator(pady=(14, 0))

        # Etiquetas de columna
        col_frame = tk.Frame(self, bg=COLORS["bg"])
        col_frame.pack(fill="x", padx=28, pady=(8, 4))

        tk.Label(
            col_frame,
            text="ESTADO",
            font=self.font_tag,
            fg=COLORS["text_muted"],
            bg=COLORS["bg"],
            width=8,
        ).pack(side="left")

        tk.Label(
            col_frame,
            text="TAREA",
            font=self.font_tag,
            fg=COLORS["text_muted"],
            bg=COLORS["bg"],
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            col_frame,
            text="HORA",
            font=self.font_tag,
            fg=COLORS["text_muted"],
            bg=COLORS["bg"],
        ).pack(side="right")

        # Lista de tareas
        list_frame = tk.Frame(self, bg=COLORS["surface"], bd=0)
        list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        # Canvas + scrollbar para lista personalizada
        self.canvas = tk.Canvas(
            list_frame,
            bg=COLORS["surface"],
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.canvas.yview,
            bg=COLORS["surface"],
            troughcolor=COLORS["surface"],
            activebackground=COLORS["accent"],
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame interior que crece
        self.task_frame = tk.Frame(self.canvas, bg=COLORS["surface"])
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.task_frame, anchor="nw"
        )

        self.task_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Mensaje cuando está vacía
        self.empty_label = tk.Label(
            self.task_frame,
            text="\n\n\n✦\n\nNo hay tareas.\nEscribe algo arriba y pulsa Enter.",
            font=self.font_empty,
            fg=COLORS["text_muted"],
            bg=COLORS["surface"],
            justify="center",
        )
        self.empty_label.pack(expand=True, pady=20)

        # Barra de estado inferior
        self._separator(pady=(0, 0))
        status_bar = tk.Frame(self, bg=COLORS["surface2"], pady=6)
        status_bar.pack(fill="x", side="bottom")

        shortcuts = [
            ("Enter", "Añadir"),
            ("C", "Completar"),
            ("Del/D", "Eliminar"),
            ("Esc", "Salir"),
        ]
        for key, label in shortcuts:
            chip = tk.Frame(status_bar, bg=COLORS["border"], padx=6, pady=2)
            chip.pack(side="left", padx=(8, 2))
            tk.Label(chip, text=key, font=self.font_tag, fg=COLORS["accent"],
                     bg=COLORS["border"]).pack(side="left")
            tk.Label(chip, text=f" {label}", font=self.font_tag,
                     fg=COLORS["text_muted"], bg=COLORS["border"]).pack(side="left")

        self.status_var = tk.StringVar(value="Listo.")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=self.font_shortcut,
            fg=COLORS["text_muted"],
            bg=COLORS["surface2"],
            padx=12,
        ).pack(side="right")

    # Widgets auxiliares

    def _separator(self, pady=(8, 8)):
        sep = tk.Frame(self, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=24, pady=pady)

    def _make_button(self, parent, text, shortcut, bg, fg, hover_bg, command):
        outer = tk.Frame(parent, bg=bg, bd=0)
        inner = tk.Frame(outer, bg=bg, padx=14, pady=8)
        inner.pack(padx=1, pady=1)

        tk.Label(inner, text=text, font=self.font_btn,
                 fg=fg, bg=bg).pack(side="left")
        tk.Label(inner, text=f"  {shortcut}", font=self.font_shortcut,
                 fg=COLORS["text_muted"], bg=bg).pack(side="left")

        def on_enter(e):
            outer.configure(bg=hover_bg)
            inner.configure(bg=hover_bg)
            for w in inner.winfo_children():
                w.configure(bg=hover_bg)

        def on_leave(e):
            outer.configure(bg=bg)
            inner.configure(bg=bg)
            for w in inner.winfo_children():
                w.configure(bg=bg)

        def on_click(e):
            command()

        for widget in [outer, inner] + inner.winfo_children():
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        return outer

    # Renderizado de lista

    def _render_tasks(self):
        # Borrar widgets actuales
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        if not self.tasks:
            self.empty_label = tk.Label(
                self.task_frame,
                text="\n\n\n✦\n\nNo hay tareas.\nEscribe algo arriba y pulsa Enter.",
                font=self.font_empty,
                fg=COLORS["text_muted"],
                bg=COLORS["surface"],
                justify="center",
            )
            self.empty_label.pack(expand=True, pady=20)
            self._update_counter()
            return

        for idx, task in enumerate(self.tasks):
            self._render_task_row(idx, task)

        self._update_counter()

    def _render_task_row(self, idx: int, task: dict):
        done = task["done"]
        selected = task.get("selected", False)

        row_bg = COLORS["done_bg"] if done else (
            COLORS["selected_bg"] if selected else COLORS["surface"]
        )

        row = tk.Frame(
            self.task_frame,
            bg=row_bg,
            pady=0,
        )
        row.pack(fill="x", padx=0, pady=0)

        # Línea separadora entre filas
        sep = tk.Frame(row, bg=COLORS["border"], height=1)
        sep.pack(fill="x")

        content = tk.Frame(row, bg=row_bg, padx=12, pady=9)
        content.pack(fill="x")

        # Columna izquierda: número + badge
        left = tk.Frame(content, bg=row_bg, width=80)
        left.pack(side="left")
        left.pack_propagate(False)

        num_label = tk.Label(
            left,
            text=f"#{idx + 1:02d}",
            font=self.font_shortcut,
            fg=COLORS["text_muted"],
            bg=row_bg,
        )
        num_label.pack(side="left", padx=(0, 6))

        if done:
            badge_bg, badge_fg, badge_txt = COLORS["success_dim"], COLORS["success"], "HECHO"
        else:
            badge_bg, badge_fg, badge_txt = COLORS["accent_dim"], COLORS["accent"], "PENDIENTE"

        badge = tk.Label(
            left,
            text=badge_txt,
            font=self.font_tag,
            fg=badge_fg,
            bg=badge_bg,
            padx=5,
            pady=2,
        )
        badge.pack(side="left")

        # Texto de la tarea
        task_text = task["text"]
        if done:
            # Tachado simulado con guiones (Tkinter no tiene tachado nativo)
            task_text = "  " + "  ".join(task_text)   # espacio entre letras

        task_fg = COLORS["done_fg"] if done else COLORS["pending"]
        task_lbl = tk.Label(
            content,
            text=task["text"],          # texto original siempre
            font=self.font_task,
            fg=task_fg,
            bg=row_bg,
            anchor="w",
            wraplength=380,
            justify="left",
        )
        # Decoración tachado: overstrike via font
        if done:
            overstrike_font = tkfont.Font(family="Consolas", size=12, overstrike=True)
            task_lbl.configure(font=overstrike_font)

        task_lbl.pack(side="left", fill="x", expand=True, padx=(12, 0))

        # Hora
        time_lbl = tk.Label(
            content,
            text=task.get("time", ""),
            font=self.font_shortcut,
            fg=COLORS["text_muted"],
            bg=row_bg,
            padx=8,
        )
        time_lbl.pack(side="right")

        # Click para seleccionar
        def select_row(event, i=idx):
            self._select_task(i)

        for w in [row, content, left, num_label, badge, task_lbl, time_lbl, sep]:
            w.bind("<Button-1>", select_row)

        # Hover
        hover_bg = "#1E1E2C" if not done else "#172A1E"

        def on_enter(e, r=row, c=content, bg=hover_bg, widgets=[left, num_label, badge, task_lbl, time_lbl]):
            if not self.tasks[idx].get("selected"):
                r.configure(bg=bg)
                c.configure(bg=bg)
                for w in widgets:
                    w.configure(bg=bg)

        def on_leave(e, r=row, c=content, bg=row_bg, widgets=[left, num_label, badge, task_lbl, time_lbl]):
            if not self.tasks[idx].get("selected"):
                r.configure(bg=bg)
                c.configure(bg=bg)
                for w in widgets:
                    w.configure(bg=bg)

        for w in [row, content, task_lbl, time_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    def _select_task(self, idx: int):
        for i, t in enumerate(self.tasks):
            t["selected"] = (i == idx)
        self._render_tasks()
        self.status_var.set(
            f"Seleccionada: «{self.tasks[idx]['text'][:40]}»"
        )

    def _get_selected_index(self) -> int | None:
        for i, t in enumerate(self.tasks):
            if t.get("selected"):
                return i
        return None

    # Acciones

    def add_task(self, event=None):
        text = self.entry_var.get().strip()
        if not text:
            self.status_var.set("⚠  Escribe una tarea primero.")
            self.entry.focus_set()
            return

        now = datetime.datetime.now().strftime("%H:%M")
        self.tasks.append({"text": text, "done": False, "selected": False, "time": now})
        self.entry_var.set("")
        self._render_tasks()
        # Seleccionar la nueva tarea
        self._select_task(len(self.tasks) - 1)
        self.status_var.set(f"✦  Tarea añadida: «{text[:40]}»")
        self.entry.focus_set()
        # Scroll abajo
        self.canvas.after(50, lambda: self.canvas.yview_moveto(1.0))

    def complete_task(self, event=None):
        idx = self._get_selected_index()
        if idx is None:
            self.status_var.set("⚠  Selecciona una tarea primero.")
            return
        task = self.tasks[idx]
        if task["done"]:
            task["done"] = False
            self.status_var.set(f"↩  Tarea reabierta: «{task['text'][:40]}»")
        else:
            task["done"] = True
            self.status_var.set(f"✔  Completada: «{task['text'][:40]}»")
        self._render_tasks()

    def delete_task(self, event=None):
        idx = self._get_selected_index()
        if idx is None:
            self.status_var.set("⚠  Selecciona una tarea primero.")
            return
        text = self.tasks[idx]["text"]
        del self.tasks[idx]
        # Seleccionar la anterior si existe
        if self.tasks:
            new_idx = min(idx, len(self.tasks) - 1)
            self.tasks[new_idx]["selected"] = True
        self._render_tasks()
        self.status_var.set(f"✕  Eliminada: «{text[:40]}»")

    def clear_completed(self, event=None):
        completed = [t for t in self.tasks if t["done"]]
        if not completed:
            self.status_var.set("No hay tareas completadas que limpiar.")
            return
        self.tasks = [t for t in self.tasks if not t["done"]]
        self._render_tasks()
        self.status_var.set(f"⊘  {len(completed)} tarea(s) completada(s) eliminadas.")

    # Atajos de teclado

    def _bind_shortcuts(self):
        # Añadir con Enter (en el entry)
        self.entry.bind("<Return>", self.add_task)

        # Atajos globales (bind en la ventana principal)
        self.bind("<KeyPress-c>",      self._shortcut_complete)
        self.bind("<KeyPress-C>",      self._shortcut_complete)
        self.bind("<Delete>",          self._shortcut_delete)
        self.bind("<KeyPress-d>",      self._shortcut_delete_key)
        self.bind("<KeyPress-D>",      self._shortcut_delete_key)
        self.bind("<Escape>",          self._shortcut_exit)

    def _shortcut_complete(self, event=None):
        # No disparar si el foco está en el Entry y el usuario escribe 'c'
        if self.focus_get() == self.entry:
            return
        self.complete_task()

    def _shortcut_delete_key(self, event=None):
        if self.focus_get() == self.entry:
            return
        self.delete_task()

    def _shortcut_delete(self, event=None):
        self.delete_task()

    def _shortcut_exit(self, event=None):
        if messagebox.askyesno(
            "Salir",
            "¿Deseas cerrar la aplicación?",
            default="yes",
        ):
            self.destroy()

    # Canvas / scroll

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Contador

    def _update_counter(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["done"])
        pending = total - done
        self.counter_var.set(
            f"{pending} pendiente(s)  ·  {done} completada(s)"
        )


# Entry point

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()