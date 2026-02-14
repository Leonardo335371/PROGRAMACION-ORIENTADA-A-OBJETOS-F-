# Sistema de gestion de inventarios

# CLASE PRODUCTO
class Producto:
    """
    Representa un producto dentro del inventario.

    Decisiones de diseño:
    - El ID se almacena como entero para facilitar comparaciones y garantizar
      unicidad numérica. No se usa UUID para mantener el sistema simple.
    - Se usan propiedades (@property) en lugar de métodos get/set explícitos,
      que es la convención idiomática de Python.
    - El precio y la cantidad validan que no sean negativos, ya que un
      producto con precio o stock negativo carece de sentido de negocio.
    """

    def __init__(self, id_producto: int, nombre: str, cantidad: int, precio: float):
        """
        Constructor del producto.
        Se llama a los setters desde el inicio para
        aprovechar la validación centralizada en un solo lugar.
        """
        self.id_producto = id_producto  # Usa el setter para validar
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    # ID
    @property
    def id_producto(self) -> int:
        return self._id_producto

    @id_producto.setter
    def id_producto(self, valor: int):
        # El ID debe ser un entero positivo; se rechaza cualquier otro valor.
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        self._id_producto = valor

    # NOMBRE
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        # Se elimina el espacio en blanco extra y se verifica que no esté vacío.
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor

    # CANTIDAD
    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        # Se permite 0 (producto agotado), pero no stock negativo.
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("La cantidad debe ser un entero no negativo.")
        self._cantidad = valor

    # PRECIO
    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float):
        # Convertimos implícitamente enteros a float para comodidad del usuario.
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número.")
        if valor < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = round(valor, 2)  # Redondeamos a 2 decimales (centavos)

    # REPRESENTACIÓN
    def __str__(self) -> str:
        """Representación legible para mostrar en consola."""
        return (
            f"  ID      : {self._id_producto}\n"
            f"  Nombre  : {self._nombre}\n"
            f"  Cantidad: {self._cantidad} unidades\n"
            f"  Precio  : ${self._precio:.2f}"
        )

    def __repr__(self) -> str:
        return (f"Producto(id={self._id_producto}, nombre='{self._nombre}', "
                f"cantidad={self._cantidad}, precio={self._precio})")


# CLASE INVENTARIO

class Inventario:
    """
    Gestiona la colección de productos de la tienda.

    Decisiones de diseño:
    - Se usa un diccionario (dict) como estructura interna con el ID como clave.
      Esto permite búsqueda por ID en O(1) frente a O(n) de una lista.
    - La búsqueda por nombre devuelve una LISTA de resultados para cubrir el
      caso de nombres similares o duplicados (supuesto del enunciado).
    - La búsqueda por nombre es case-insensitive para mejorar la usabilidad.
    """

    def __init__(self):
        # Diccionario: { id_producto (int) -> Producto }
        self._productos: dict[int, Producto] = {}

    # AÑADIR
    def añadir_producto(self, producto: Producto) -> bool:
        """
        Añade un producto al inventario.
        Retorna True si se añadió, False si el ID ya existía.
        Se prefiere retornar un booleano en lugar de lanzar una excepción
        porque la duplicación de ID es un flujo de usuario normal, no un error.
        """
        if producto.id_producto in self._productos:
            return False  # ID duplicado: no se añade
        self._productos[producto.id_producto] = producto
        return True

    # ELIMINAR
    def eliminar_producto(self, id_producto: int) -> bool:
        """
        Elimina un producto por ID.
        Retorna True si se eliminó, False si no existía.
        """
        if id_producto not in self._productos:
            return False
        del self._productos[id_producto]
        return True

    # ACTUALIZAR
    def actualizar_producto(
        self,
        id_producto: int,
        nueva_cantidad: int | None = None,
        nuevo_precio: float | None = None
    ) -> bool:
        """
        Actualiza la cantidad y/o el precio de un producto por ID.
        Acepta None en los parámetros para actualizar solo uno de los dos.
        Retorna True si se actualizó, False si el ID no existe.
        """
        if id_producto not in self._productos:
            return False
        producto = self._productos[id_producto]
        if nueva_cantidad is not None:
            producto.cantidad = nueva_cantidad  # El setter valida el valor
        if nuevo_precio is not None:
            producto.precio = nuevo_precio       # El setter valida el valor
        return True

    # BUSCAR POR NOMBRE
    def buscar_por_nombre(self, nombre: str) -> list[Producto]:
        """
        Devuelve una lista de productos cuyo nombre contenga la cadena buscada
        (búsqueda parcial, case-insensitive).
        Supuesto: se prefiere búsqueda de subcadena en lugar de coincidencia
        exacta para que el usuario pueda encontrar resultados con consultas
        parciales (p. ej., 'manz' encuentre 'Manzana roja').
        """
        termino = nombre.strip().lower()
        return [p for p in self._productos.values()
                if termino in p.nombre.lower()]

    # MOSTRAR TODOS
    def mostrar_todos(self) -> list[Producto]:
        """
        Retorna la lista completa de productos ordenados por ID.
        Se ordena por ID para presentar una visualización consistente.
        """
        return sorted(self._productos.values(), key=lambda p: p.id_producto)

    def esta_vacio(self) -> bool:
        """Utilidad para verificar si el inventario no tiene productos."""
        return len(self._productos) == 0

    def id_existe(self, id_producto: int) -> bool:
        """Comprueba si un ID ya está registrado (útil para la UI)."""
        return id_producto in self._productos

    def siguiente_id(self) -> int:
        """
        Sugiere el próximo ID disponible (máximo actual + 1).
        Facilita al usuario saber qué ID puede usar sin adivinar.
        """
        if self.esta_vacio():
            return 1
        return max(self._productos.keys()) + 1


# INTERFAZ DE USUARIO EN CONSOLA

# Constantes de presentación
LINEA = "=" * 55
SEPARADOR = "-" * 55


def limpiar_pantalla():
    """Imprime líneas en blanco para simular limpieza de pantalla."""
    print("\n" * 2)


def pausar():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\n  Presione Enter para continuar...")


def encabezado(titulo: str):
    """Imprime un encabezado formateado para cada sección del menú."""
    print(f"\n{LINEA}")
    print(f"  {titulo}")
    print(LINEA)


# Funciones de entrada segura

def pedir_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    """
    Solicita un entero al usuario con validación de rango opcional.
    Repite la solicitud hasta obtener un valor válido.
    """
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠ Ingrese un valor mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f" ⚠ Ingrese un valor menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠ Entrada inválida. Ingrese un número entero.")


def pedir_flotante(mensaje: str, minimo: float = 0.0) -> float:
    """
    Solicita un número decimal al usuario con validación de mínimo.
    """
    while True:
        try:
            valor = float(input(mensaje))
            if valor < minimo:
                print(f"  ⚠ Ingrese un valor mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠ Entrada inválida. Ingrese un número (ej: 9.99).")


def pedir_texto(mensaje: str) -> str:
    """Solicita una cadena no vacía al usuario."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  ⚠ Este campo no puede estar vacío.")


# Operaciones del menú

def op_añadir(inventario: Inventario):
    """Flujo completo para añadir un nuevo producto."""
    encabezado("AÑADIR PRODUCTO")
    print(f"  (Próximo ID sugerido: {inventario.siguiente_id()})")

    id_p = pedir_entero("  ID del producto   : ", minimo=1)

    # Verificamos duplicado antes de pedir más datos al usuario
    if inventario.id_existe(id_p):
        print(f"\n  ✗ Ya existe un producto con ID {id_p}. Operación cancelada.")
        pausar()
        return

    nombre = pedir_texto("  Nombre            : ")
    cantidad = pedir_entero("  Cantidad inicial  : ", minimo=0)
    precio = pedir_flotante("  Precio unitario   : $", minimo=0.0)

    try:
        nuevo = Producto(id_p, nombre, cantidad, precio)
        inventario.añadir_producto(nuevo)
        print(f"\n  ✔ Producto '{nombre}' añadido con éxito.")
    except ValueError as e:
        # Capturamos errores inesperados de validación (p. ej., datos de borde)
        print(f"\n  ✗ Error al crear producto: {e}")

    pausar()


def op_eliminar(inventario: Inventario):
    """Flujo para eliminar un producto por ID con confirmación."""
    encabezado("ELIMINAR PRODUCTO")

    if inventario.esta_vacio():
        print("  El inventario está vacío. No hay productos para eliminar.")
        pausar()
        return

    id_p = pedir_entero("  ID del producto a eliminar: ", minimo=1)

    # Mostramos el producto antes de pedir confirmación
    resultados = [p for p in inventario.mostrar_todos() if p.id_producto == id_p]
    if not resultados:
        print(f"\n  ✗ No se encontró ningún producto con ID {id_p}.")
        pausar()
        return

    print(f"\n  Producto encontrado:\n{resultados[0]}")
    confirmar = input("\n  ¿Confirma la eliminación? (s/n): ").strip().lower()

    if confirmar == "s":
        inventario.eliminar_producto(id_p)
        print(f"\n  ✔ Producto con ID {id_p} eliminado correctamente.")
    else:
        print("  Operación cancelada.")

    pausar()


def op_actualizar(inventario: Inventario):
    """Flujo para actualizar cantidad y/o precio de un producto."""
    encabezado("ACTUALIZAR PRODUCTO")

    if inventario.esta_vacio():
        print("  El inventario está vacío. No hay productos para actualizar.")
        pausar()
        return

    id_p = pedir_entero("  ID del producto a actualizar: ", minimo=1)

    if not inventario.id_existe(id_p):
        print(f"\n  ✗ No se encontró ningún producto con ID {id_p}.")
        pausar()
        return

    # Mostramos el estado actual para que el usuario sepa qué valores cambiar
    producto_actual = [p for p in inventario.mostrar_todos() if p.id_producto == id_p][0]
    print(f"\n  Estado actual:\n{producto_actual}")
    print(f"\n  {SEPARADOR}")
    print("  Deje en blanco y presione Enter para mantener el valor actual.")

    # Actualizar cantidad
    nueva_cantidad = None
    entrada = input(f"  Nueva cantidad [{producto_actual.cantidad}]: ").strip()
    if entrada:
        try:
            nueva_cantidad = int(entrada)
            if nueva_cantidad < 0:
                print("  ⚠ Cantidad inválida; se mantendrá el valor anterior.")
                nueva_cantidad = None
        except ValueError:
            print("  ⚠ Valor no numérico; se mantendrá el valor anterior.")

    # Actualizar precio
    nuevo_precio = None
    entrada = input(f"  Nuevo precio [${producto_actual.precio:.2f}]: $").strip()
    if entrada:
        try:
            nuevo_precio = float(entrada)
            if nuevo_precio < 0:
                print("  ⚠ Precio inválido; se mantendrá el valor anterior.")
                nuevo_precio = None
        except ValueError:
            print("  ⚠ Valor no numérico; se mantendrá el valor anterior.")

    if nueva_cantidad is None and nuevo_precio is None:
        print("\n  No se realizaron cambios.")
    else:
        inventario.actualizar_producto(id_p, nueva_cantidad, nuevo_precio)
        print("\n  ✔ Producto actualizado con éxito.")

    pausar()


def op_buscar(inventario: Inventario):
    """Flujo para buscar productos por nombre (parcial, sin distinción de mayúsculas)."""
    encabezado("BUSCAR PRODUCTO")

    if inventario.esta_vacio():
        print("  El inventario está vacío. No hay productos para buscar.")
        pausar()
        return

    termino = pedir_texto("  Nombre o fragmento a buscar: ")
    resultados = inventario.buscar_por_nombre(termino)

    if not resultados:
        print(f"\n  ✗ No se encontraron productos que contengan '{termino}'.")
    else:
        print(f"\n  Se encontraron {len(resultados)} resultado(s):\n")
        for p in resultados:
            print(p)
            print(f"  {SEPARADOR}")

    pausar()


def op_mostrar_todos(inventario: Inventario):
    """Muestra todos los productos ordenados por ID."""
    encabezado("TODOS LOS PRODUCTOS")

    if inventario.esta_vacio():
        print("  El inventario está vacío.")
        pausar()
        return

    productos = inventario.mostrar_todos()
    print(f"  Total de productos: {len(productos)}\n")

    for p in productos:
        print(p)
        print(f"  {SEPARADOR}")

    pausar()


def mostrar_menu():
    """Imprime el menú principal de opciones."""
    print(f"\n{LINEA}")
    print("       SISTEMA DE GESTIÓN DE INVENTARIOS")
    print(LINEA)
    print("  1. Añadir producto")
    print("  2. Eliminar producto")
    print("  3. Actualizar cantidad / precio")
    print("  4. Buscar producto por nombre")
    print("  5. Mostrar todos los productos")
    print("  0. Salir")
    print(LINEA)


# Punto de entrada

def main():
    """
    Función principal que ejecuta el ciclo de vida de la aplicación.
    Se pre-carga el inventario con datos de ejemplo para facilitar las pruebas.
    """
    inventario = Inventario()

    # Datos de ejemplo para que el usuario pueda probar el sistema de inmediato
    datos_ejemplo = [
        Producto(1, "Manzana Roja",  100, 0.50),
        Producto(2, "Manzana Verde",  80, 0.55),
        Producto(3, "Leche Entera",   50, 1.20),
        Producto(4, "Pan Integral",   30, 2.50),
        Producto(5, "Jugo de Naranja", 20, 3.75),
    ]
    for p in datos_ejemplo:
        inventario.añadir_producto(p)

    print("\n  Bienvenido al Sistema de Gestión de Inventarios.")
    print("  (Se han cargado 5 productos de ejemplo para comenzar.)")

    # Ciclo principal del menú: continúa hasta que el usuario elija salir (0)
    while True:
        mostrar_menu()
        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            op_añadir(inventario)
        elif opcion == "2":
            op_eliminar(inventario)
        elif opcion == "3":
            op_actualizar(inventario)
        elif opcion == "4":
            op_buscar(inventario)
        elif opcion == "5":
            op_mostrar_todos(inventario)
        elif opcion == "0":
            print("\n  ¡Hasta luego! Sistema cerrado correctamente.\n")
            break
        else:
            # Cualquier entrada no reconocida muestra un aviso sin crashear
            print("  ⚠ Opción no válida. Ingrese un número del 0 al 5.")


# Punto de entrada estándar de Python: solo se ejecuta si se corre directamente
if __name__ == "__main__":
    main()