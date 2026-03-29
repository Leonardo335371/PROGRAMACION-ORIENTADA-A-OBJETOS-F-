"""
  APLICACIÓN GUI - LISTA DE TAREAS
 
  Funcionalidades:
    - Añadir tareas con botón o tecla Enter
    - Marcar tareas como completadas (doble clic o botón)
    - Eliminar tareas seleccionadas
    - Indicador visual de estado (✓ completada / ○ pendiente)
"""

import tkinter as tk
from tkinter import messagebox, font


#  CLASE PRINCIPAL DE LA APLICACIÓN
class ListaDeTareas:
    """
    Gestiona la lógica y la interfaz gráfica de la
    lista de tareas utilizando Tkinter.
    """

    # Paleta de colores centralizada para mantener coherencia visual
    COLORES = {
        "fondo":        "#1A1A2E",   # Fondo oscuro principal
        "panel":        "#16213E",   # Panel lateral / cabecera
        "acento":       "#E94560",   # Rojo-rosa para acciones principales
        "acento2":      "#0F3460",   # Azul oscuro para acciones secundarias
        "texto":        "#E0E0E0",   # Texto principal claro
        "texto_dim":    "#888888",   # Texto secundario / placeholder
        "completada":   "#4CAF50",   # Verde para tareas completadas
        "item_bg":      "#0D1B2A",   # Fondo de cada ítem de la lista
        "item_hover":   "#1B2B3A",   # Hover sobre un ítem
        "borde":        "#2A2A4A",   # Bordes sutiles
    }

    def __init__(self, raiz: tk.Tk):
        """
        Constructor: recibe la ventana raíz y construye
        todos los widgets de la interfaz.
        """
        self.raiz = raiz
        self._configurar_ventana()
        self._construir_ui()
        self._vincular_eventos_globales()

    # Configuración de la ventana
    def _configurar_ventana(self):
        """Establece título, tamaño y estilo de la ventana principal."""
        self.raiz.title("✅ Lista de Tareas")
        self.raiz.geometry("520x680")
        self.raiz.resizable(False, False)
        self.raiz.configure(bg=self.COLORES["fondo"])

        # Centrar la ventana en la pantalla
        self.raiz.update_idletasks()
        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla  = self.raiz.winfo_screenheight()
        x = (ancho_pantalla - 520) // 2
        y = (alto_pantalla  - 680) // 2
        self.raiz.geometry(f"520x680+{x}+{y}")

    # Construcción de la UI
    def _construir_ui(self):
        """Crea y organiza todos los componentes visuales."""
        self._crear_cabecera()
        self._crear_campo_entrada()
        self._crear_lista()
        self._crear_botones()
        self._crear_pie()

    def _crear_cabecera(self):
        """Panel superior con título y contador de tareas pendientes."""
        frame = tk.Frame(self.raiz, bg=self.COLORES["panel"], pady=20)
        frame.pack(fill="x")

        # Título principal
        tk.Label(
            frame,
            text="📋  MIS TAREAS",
            font=("Courier New", 22, "bold"),
            fg=self.COLORES["acento"],
            bg=self.COLORES["panel"],
        ).pack()

        # Subtítulo / contador dinámico
        self.lbl_contador = tk.Label(
            frame,
            text="No hay tareas aún",
            font=("Courier New", 10),
            fg=self.COLORES["texto_dim"],
            bg=self.COLORES["panel"],
        )
        self.lbl_contador.pack(pady=(4, 0))

    def _crear_campo_entrada(self):
        """Frame con Entry + botón 'Añadir Tarea'."""
        frame = tk.Frame(self.raiz, bg=self.COLORES["fondo"], padx=20, pady=16)
        frame.pack(fill="x")

        # Campo de texto
        # Se guarda como atributo para acceder desde los manejadores
        self.entrada = tk.Entry(
            frame,
            font=("Courier New", 12),
            bg=self.COLORES["item_bg"],
            fg=self.COLORES["texto"],
            insertbackground=self.COLORES["acento"],  # Cursor visible
            relief="flat",
            bd=0,
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))

        # Texto placeholder (simulado, ya que Tkinter no lo incluye nativamente)
        self._placeholder = "Escribe una tarea..."
        self._mostrar_placeholder()

        # Botón Añadir
        btn_anadir = tk.Button(
            frame,
            text="＋ Añadir",
            font=("Courier New", 11, "bold"),
            bg=self.COLORES["acento"],
            fg="white",
            activebackground="#C73652",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=10,
            cursor="hand2",
            command=self._anadir_tarea,  # Manejador de evento: clic en botón
        )
        btn_anadir.pack(side="right")

    def _crear_lista(self):
        """Listbox con scrollbar para mostrar las tareas."""
        frame = tk.Frame(self.raiz, bg=self.COLORES["fondo"], padx=20)
        frame.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Listbox
        self.listbox = tk.Listbox(
            frame,
            font=("Courier New", 12),
            bg=self.COLORES["item_bg"],
            fg=self.COLORES["texto"],
            selectbackground=self.COLORES["acento2"],
            selectforeground="white",
            activestyle="none",        # Sin subrayado en ítem activo
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COLORES["borde"],
            highlightbackground=self.COLORES["borde"],
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

    def _crear_botones(self):
        """Fila de botones: Marcar completada y Eliminar."""
        frame = tk.Frame(self.raiz, bg=self.COLORES["fondo"], padx=20, pady=12)
        frame.pack(fill="x")

        # Botón: Marcar como Completada
        btn_completar = tk.Button(
            frame,
            text="✔  Marcar Completada",
            font=("Courier New", 11),
            bg=self.COLORES["acento2"],
            fg=self.COLORES["texto"],
            activebackground="#1A4A80",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self._marcar_completada,  # Manejador: clic en botón
        )
        btn_completar.pack(side="left", expand=True, fill="x", padx=(0, 6))

        # Botón: Eliminar Tarea
        btn_eliminar = tk.Button(
            frame,
            text="✖  Eliminar",
            font=("Courier New", 11),
            bg="#3D1A1A",
            fg=self.COLORES["texto"],
            activebackground="#5C2222",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self._eliminar_tarea,  # Manejador: clic en botón
        )
        btn_eliminar.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _crear_pie(self):
        """Barra inferior con instrucciones de uso."""
        frame = tk.Frame(self.raiz, bg=self.COLORES["panel"], pady=8)
        frame.pack(fill="x", side="bottom")

        tk.Label(
            frame,
            text="Enter: añadir  •  Doble clic: completar  •  Supr: eliminar",
            font=("Courier New", 9),
            fg=self.COLORES["texto_dim"],
            bg=self.COLORES["panel"],
        ).pack()

    # Eventos globales
    def _vincular_eventos_globales(self):
        """
        Asocia atajos de teclado y eventos del ratón
        a sus respectivos manejadores.
        """
        # Enter en el campo de entrada → añadir tarea
        self.entrada.bind("<Return>", lambda e: self._anadir_tarea())

        # Doble clic en la lista → marcar como completada
        self.listbox.bind("<Double-Button-1>", lambda e: self._marcar_completada())

        # Tecla Supr (Delete) → eliminar tarea seleccionada
        self.listbox.bind("<Delete>", lambda e: self._eliminar_tarea())

        # Placeholder: limpiar al enfocar, restaurar al desenfocar
        self.entrada.bind("<FocusIn>",  self._limpiar_placeholder)
        self.entrada.bind("<FocusOut>", self._restaurar_placeholder)

    # Lógica: Placeholder
    def _mostrar_placeholder(self):
        """Inserta el texto de ayuda en el Entry con color tenue."""
        self.entrada.insert(0, self._placeholder)
        self.entrada.config(fg=self.COLORES["texto_dim"])

    def _limpiar_placeholder(self, evento=None):
        """Al recibir foco, elimina el placeholder si está presente."""
        if self.entrada.get() == self._placeholder:
            self.entrada.delete(0, "end")
            self.entrada.config(fg=self.COLORES["texto"])

    def _restaurar_placeholder(self, evento=None):
        """Al perder foco, muestra el placeholder si el campo está vacío."""
        if not self.entrada.get().strip():
            self._mostrar_placeholder()

    # Lógica: Gestión de tareas
    def _anadir_tarea(self):
        """
        Manejador para el evento 'Añadir Tarea'.
        Valida la entrada y añade la nueva tarea a la lista.
        """
        texto = self.entrada.get().strip()

        # Ignorar si el campo está vacío o contiene el placeholder
        if not texto or texto == self._placeholder:
            self.entrada.focus_set()  # Devolver el foco al campo
            return

        # Formato: ○ indica tarea pendiente
        self.listbox.insert("end", f"  ○  {texto}")

        # Restaurar el campo de entrada
        self.entrada.delete(0, "end")
        self.entrada.focus_set()

        # Actualizar el contador en la cabecera
        self._actualizar_contador()

    def _marcar_completada(self):
        """
        Manejador para el evento 'Marcar Completada'.
        Alterna el estado visual de la tarea seleccionada:
        pendiente (○) ↔ completada (✓).
        """
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona una tarea primero.")
            return

        indice = seleccion[0]
        texto_actual = self.listbox.get(indice)

        if "○" in texto_actual:
            # Tarea pendiente → marcar como completada
            nuevo_texto = texto_actual.replace("○", "✓")
            self.listbox.delete(indice)
            self.listbox.insert(indice, nuevo_texto)
            # Cambiar color para feedback visual de completada
            self.listbox.itemconfig(indice, fg=self.COLORES["completada"])
        else:
            # Tarea completada → revertir a pendiente
            nuevo_texto = texto_actual.replace("✓", "○")
            self.listbox.delete(indice)
            self.listbox.insert(indice, nuevo_texto)
            self.listbox.itemconfig(indice, fg=self.COLORES["texto"])

        # Mantener la selección en el mismo ítem
        self.listbox.selection_set(indice)
        self._actualizar_contador()

    def _eliminar_tarea(self):
        """
        Manejador para el evento 'Eliminar Tarea'.
        Pide confirmación y elimina la tarea seleccionada.
        """
        seleccion = self.listbox.curselection()

        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona una tarea primero.")
            return

        indice = seleccion[0]
        nombre = self.listbox.get(indice).replace("  ○  ", "").replace("  ✓  ", "").strip()

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar la tarea:\n\n«{nombre}»?",
        )

        if confirmar:
            self.listbox.delete(indice)
            self._actualizar_contador()

    def _actualizar_contador(self):
        """Actualiza el label de la cabecera con las estadísticas actuales."""
        total      = self.listbox.size()
        completadas = sum(
            1 for i in range(total) if "✓" in self.listbox.get(i)
        )
        pendientes = total - completadas

        if total == 0:
            texto = "No hay tareas aún"
        else:
            texto = f"{total} tarea{'s' if total != 1 else ''}  •  "
            texto += f"{pendientes} pendiente{'s' if pendientes != 1 else ''}  •  "
            texto += f"{completadas} completada{'s' if completadas != 1 else ''}"

        self.lbl_contador.config(text=texto)


#  PUNTO DE ENTRADA
if __name__ == "__main__":
    raiz = tk.Tk()
    app  = ListaDeTareas(raiz)
    raiz.mainloop()