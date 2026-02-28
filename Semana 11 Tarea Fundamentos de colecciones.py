"""
  SISTEMA AVANZADO DE GESTIÓN DE INVENTARIOS

Arquitectura del sistema:
  - Clase Producto: Representa cada ítem del inventario.
  - Clase Inventario: Gestiona la colección de productos usando un
    diccionario {id: Producto} para búsqueda O(1).
  - Persistencia: Serialización a JSON para lectura/escritura en disco.
  - Colecciones utilizadas:
      • dict  → almacén principal del inventario (O(1) por ID)
      • list  → resultados de búsqueda y listados
      • set   → registro de IDs usados (evita duplicados)
      • tuple → datos inmutables de historial de cambios
"""

import json
import os
from datetime import datetime


#  CLASE PRODUCTO

class Producto:
    """
    Representa un producto del inventario.

    Atributos (privados, accesibles con getters/setters):
        _id       (str)   : Identificador único.
        _nombre   (str)   : Nombre descriptivo del producto.
        _cantidad (int)   : Unidades disponibles en stock.
        _precio   (float) : Precio unitario.

    Uso de colecciones internas:
        _historial (list[tuple]) : Registro inmutable de modificaciones.
            Cada entrada es una tupla (campo_modificado, valor_anterior,
            valor_nuevo, timestamp), lo que garantiza integridad histórica.
    """

    def __init__(self, id_producto: str, nombre: str,
                 cantidad: int, precio: float):
        # Validaciones básicas en la construcción
        if not id_producto or not isinstance(id_producto, str):
            raise ValueError("El ID debe ser una cadena no vacía.")
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")

        self._id = id_producto.upper().strip()
        self._nombre = nombre.strip()
        self._cantidad = int(cantidad)
        self._precio = float(precio)
        # Historial: lista de tuplas (campo, antes, después, momento)
        self._historial: list[tuple] = []

    # Getters 
    def get_id(self) -> str:
        return self._id

    def get_nombre(self) -> str:
        return self._nombre

    def get_cantidad(self) -> int:
        return self._cantidad

    def get_precio(self) -> float:
        return self._precio

    def get_historial(self) -> list:
        """Devuelve una copia del historial para proteger la integridad."""
        return list(self._historial)

    # Setters con validación y registro 
    def set_nombre(self, nuevo_nombre: str) -> None:
        anterior = self._nombre
        self._nombre = nuevo_nombre.strip()
        self._registrar_cambio("nombre", anterior, self._nombre)

    def set_cantidad(self, nueva_cantidad: int) -> None:
        if nueva_cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        anterior = self._cantidad
        self._cantidad = int(nueva_cantidad)
        self._registrar_cambio("cantidad", anterior, self._cantidad)

    def set_precio(self, nuevo_precio: float) -> None:
        if nuevo_precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        anterior = self._precio
        self._precio = float(nuevo_precio)
        self._registrar_cambio("precio", anterior, self._precio)

    # ── Métodos de utilidad 
    def _registrar_cambio(self, campo: str, antes, despues) -> None:
        """Agrega una tupla inmutable al historial de cambios."""
        entrada: tuple = (campo, antes, despues,
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self._historial.append(entrada)

    def valor_total(self) -> float:
        """Retorna el valor total del stock de este producto."""
        return round(self._cantidad * self._precio, 2)

    def to_dict(self) -> dict:
        """Serializa el producto a diccionario para guardarlo en JSON."""
        return {
            "id": self._id,
            "nombre": self._nombre,
            "cantidad": self._cantidad,
            "precio": self._precio,
            # El historial se serializa como lista de listas (JSON no tiene tuplas)
            "historial": [list(h) for h in self._historial]
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Producto":
        """Deserializa un diccionario JSON → objeto Producto."""
        p = cls(datos["id"], datos["nombre"],
                datos["cantidad"], datos["precio"])
        # Restaura el historial como lista de tuplas
        p._historial = [tuple(h) for h in datos.get("historial", [])]
        return p

    def __str__(self) -> str:
        return (f"[{self._id}] {self._nombre:<30} "
                f"Cant: {self._cantidad:>6}  "
                f"Precio: ${self._precio:>10.2f}  "
                f"Total: ${self.valor_total():>12.2f}")

    def __repr__(self) -> str:
        return (f"Producto(id={self._id!r}, nombre={self._nombre!r}, "
                f"cantidad={self._cantidad}, precio={self._precio})")


# CLASE INVENTARIO

class Inventario:
    """
    Gestiona la colección completa de productos.

    Colecciones internas y su propósito:
        _productos (dict)  : {ID → Producto}. Permite acceso O(1) por ID.
            Es la estructura principal de almacenamiento.
        _ids_usados (set)  : Conjunto de IDs ya empleados (incluye eliminados).
            Garantiza unicidad histórica y evita reutilizar IDs.
        _categorias (dict) : {categoría → set(IDs)}. Índice secundario que
            permite agrupar y filtrar productos por categoría en O(1).
    """

    ARCHIVO_PREDETERMINADO = "inventario.json"

    def __init__(self, archivo: str = ARCHIVO_PREDETERMINADO):
        self._productos: dict[str, Producto] = {}
        self._ids_usados: set[str] = set()          # IDs históricos (nunca se reducen)
        self._categorias: dict[str, set] = {}        # índice de categorías
        self._archivo = archivo
        # Intentamos cargar datos persistidos al iniciar
        self._cargar_desde_archivo()

    #  OPERACIONES CRUD

    def agregar_producto(self, id_producto: str, nombre: str,
                         cantidad: int, precio: float,
                         categoria: str = "General") -> bool:
        """
        Añade un nuevo producto al inventario.

        Lógica:
          1. Verificar que el ID no exista (busca en dict O(1)).
          2. Crear instancia Producto.
          3. Insertar en _productos (dict) y actualizar _ids_usados (set).
          4. Actualizar índice _categorias (dict de sets).

        Returns:
            True si se agregó correctamente, False en caso contrario.
        """
        id_upper = id_producto.upper().strip()
        if id_upper in self._productos:
            print(f"  ✗ Ya existe un producto con ID '{id_upper}'.")
            return False
        if id_upper in self._ids_usados:
            print(f"  ✗ El ID '{id_upper}' fue usado anteriormente y está reservado.")
            return False

        try:
            nuevo = Producto(id_upper, nombre, cantidad, precio)
        except ValueError as e:
            print(f"  ✗ Error de validación: {e}")
            return False

        self._productos[id_upper] = nuevo
        self._ids_usados.add(id_upper)          # Actualiza el set de IDs
        # Actualiza el índice de categorías
        cat = categoria.strip().title()
        if cat not in self._categorias:
            self._categorias[cat] = set()
        self._categorias[cat].add(id_upper)

        self._guardar_en_archivo()
        print(f"  ✓ Producto '{nombre}' (ID: {id_upper}) agregado exitosamente.")
        return True

    def eliminar_producto(self, id_producto: str) -> bool:
        """
        Elimina un producto por su ID.
        El ID permanece en _ids_usados para evitar su reutilización.
        """
        id_upper = id_producto.upper().strip()
        if id_upper not in self._productos:
            print(f"  ✗ No se encontró producto con ID '{id_upper}'.")
            return False

        nombre = self._productos[id_upper].get_nombre()
        del self._productos[id_upper]           # O(1) en dict
        # Nota: NO removemos de _ids_usados → el ID queda reservado

        # Limpiar del índice de categorías
        for ids_cat in self._categorias.values():
            ids_cat.discard(id_upper)           # discard en set no lanza error

        self._guardar_en_archivo()
        print(f"  ✓ Producto '{nombre}' (ID: {id_upper}) eliminado del inventario.")
        return True

    def actualizar_producto(self, id_producto: str,
                            nueva_cantidad: int = None,
                            nuevo_precio: float = None) -> bool:
        """
        Actualiza cantidad y/o precio de un producto existente.
        Acepta actualización parcial: se puede modificar solo uno de los campos.
        """
        id_upper = id_producto.upper().strip()
        if id_upper not in self._productos:
            print(f"  ✗ No se encontró producto con ID '{id_upper}'.")
            return False

        producto = self._productos[id_upper]
        actualizado = False

        if nueva_cantidad is not None:
            try:
                producto.set_cantidad(nueva_cantidad)
                print(f"  ✓ Cantidad actualizada a {nueva_cantidad}.")
                actualizado = True
            except ValueError as e:
                print(f"  ✗ Error en cantidad: {e}")

        if nuevo_precio is not None:
            try:
                producto.set_precio(nuevo_precio)
                print(f"  ✓ Precio actualizado a ${nuevo_precio:.2f}.")
                actualizado = True
            except ValueError as e:
                print(f"  ✗ Error en precio: {e}")

        if actualizado:
            self._guardar_en_archivo()
        return actualizado

    #  BÚSQUEDA Y CONSULTA

    def buscar_por_nombre(self, termino: str) -> list[Producto]:
        """
        Búsqueda parcial e insensible a mayúsculas por nombre de producto.

        Implementación:
            Itera sobre los valores del dict (_productos.values()) y construye
            una lista de resultados. Para inventarios grandes se podría
            mantener un índice invertido; aquí O(n) es aceptable.

        Returns:
            Lista de objetos Producto que coinciden con el término.
        """
        termino_lower = termino.lower().strip()
        # List comprehension sobre los valores del diccionario
        resultados: list[Producto] = [
            p for p in self._productos.values()
            if termino_lower in p.get_nombre().lower()
        ]
        return resultados

    def buscar_por_id(self, id_producto: str) -> Producto | None:
        """Búsqueda directa O(1) por ID en el diccionario."""
        return self._productos.get(id_producto.upper().strip())

    def buscar_por_categoria(self, categoria: str) -> list[Producto]:
        """
        Devuelve todos los productos de una categoría usando el índice
        _categorias (dict de sets) para acceso eficiente.
        """
        cat = categoria.strip().title()
        ids = self._categorias.get(cat, set())
        # Reconstruye la lista a partir de los IDs del set
        return [self._productos[i] for i in ids if i in self._productos]

    def mostrar_todos(self) -> None:
        """Muestra todos los productos ordenados por nombre."""
        if not self._productos:
            print("  El inventario está vacío.")
            return
        # Ordena los valores del dict por nombre (genera una lista temporal)
        productos_ordenados: list[Producto] = sorted(
            self._productos.values(), key=lambda p: p.get_nombre()
        )
        print(f"\n{'─'*80}")
        print(f"  {'ID':<10} {'NOMBRE':<30} {'CANT':>6}  {'PRECIO':>12}  {'TOTAL':>14}")
        print(f"{'─'*80}")
        for p in productos_ordenados:
            print(f"  {p}")
        print(f"{'─'*80}")
        print(f"  Total de productos: {len(self._productos)} | "
              f"Valor total del inventario: ${self.valor_total_inventario():,.2f}\n")

    def mostrar_historial(self, id_producto: str) -> None:
        """Muestra el historial de cambios de un producto."""
        producto = self.buscar_por_id(id_producto)
        if not producto:
            print(f"  ✗ No se encontró producto con ID '{id_producto.upper()}'.")
            return
        historial = producto.get_historial()
        if not historial:
            print(f"  Sin cambios registrados para '{producto.get_nombre()}'.")
            return
        print(f"\n  Historial de '{producto.get_nombre()}':")
        for campo, antes, despues, momento in historial:
            print(f"    [{momento}] {campo}: {antes} → {despues}")

    def mostrar_categorias(self) -> None:
        """Muestra el índice de categorías con conteo de productos."""
        if not self._categorias:
            print("  No hay categorías registradas.")
            return
        print("\n  Categorías:")
        for cat, ids in sorted(self._categorias.items()):
            activos = len([i for i in ids if i in self._productos])
            print(f"    • {cat:<20} {activos} producto(s)")

    def valor_total_inventario(self) -> float:
        """Suma el valor total de todos los productos."""
        return round(sum(p.valor_total() for p in self._productos.values()), 2)

    #  PERSISTENCIA EN ARCHIVOS (JSON)

    def _guardar_en_archivo(self) -> None:
        """
        Serialización del inventario a JSON.

        Estructura del archivo:
        {
          "metadata": { "total_productos": int, "ultimo_guardado": str },
          "ids_usados": [lista de todos los IDs históricos],
          "categorias": { "Cat": ["ID1", "ID2"] },
          "productos": [ { ...datos_producto... }, ... ]
        }

        Se usan listas en lugar de sets/dicts porque JSON no soporta
        estos tipos directamente.
        """
        datos = {
            "metadata": {
                "total_productos": len(self._productos),
                "ultimo_guardado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            # Convertimos set → list para JSON
            "ids_usados": sorted(list(self._ids_usados)),
            # Convertimos dict de sets → dict de listas para JSON
            "categorias": {
                cat: sorted(list(ids))
                for cat, ids in self._categorias.items()
            },
            # Serializa cada producto usando su método to_dict()
            "productos": [p.to_dict() for p in self._productos.values()]
        }
        try:
            with open(self._archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"  ⚠ Advertencia: No se pudo guardar el archivo: {e}")

    def _cargar_desde_archivo(self) -> None:
        """
        Deserialización del inventario desde JSON.

        Proceso inverso a _guardar_en_archivo():
          1. Lee el JSON.
          2. Restaura _ids_usados como set (desde lista JSON).
          3. Restaura _categorias como dict de sets (desde dict de listas).
          4. Reconstruye cada Producto usando Producto.from_dict().
        """
        if not os.path.exists(self._archivo):
            return  # Archivo nuevo; comienza con inventario vacío

        try:
            with open(self._archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Restaura el set de IDs usados
            self._ids_usados = set(datos.get("ids_usados", []))

            # Restaura el índice de categorías (dict de sets)
            self._categorias = {
                cat: set(ids)
                for cat, ids in datos.get("categorias", {}).items()
            }

            # Reconstruye los objetos Producto
            self._productos = {}
            for d in datos.get("productos", []):
                p = Producto.from_dict(d)
                self._productos[p.get_id()] = p

            total = len(self._productos)
            if total:
                print(f"  ✓ Inventario cargado: {total} producto(s) desde '{self._archivo}'.")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠ Error al leer el archivo de inventario: {e}")
            print("     Se iniciará con un inventario vacío.")


#  INTERFAZ DE USUARIO (MENÚ INTERACTIVO)

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n  Presiona ENTER para continuar...")


def solicitar_entero(mensaje: str, minimo: int = 0) -> int | None:
    """Solicita un entero al usuario con validación."""
    entrada = input(mensaje).strip()
    if not entrada:
        return None
    try:
        valor = int(entrada)
        if valor < minimo:
            print(f"  ✗ El valor mínimo es {minimo}.")
            return None
        return valor
    except ValueError:
        print("  ✗ Ingresa un número entero válido.")
        return None


def solicitar_flotante(mensaje: str, minimo: float = 0.0) -> float | None:
    """Solicita un número flotante al usuario con validación."""
    entrada = input(mensaje).strip()
    if not entrada:
        return None
    try:
        valor = float(entrada)
        if valor < minimo:
            print(f"  ✗ El valor mínimo es {minimo}.")
            return None
        return valor
    except ValueError:
        print("  ✗ Ingresa un número válido.")
        return None


def menu_agregar(inv: Inventario) -> None:
    print("\n  ── AGREGAR PRODUCTO ───")
    id_prod = input("  ID del producto     : ").strip()
    if not id_prod:
        print("  ✗ El ID no puede estar vacío.")
        return
    nombre = input("  Nombre              : ").strip()
    if not nombre:
        print("  ✗ El nombre no puede estar vacío.")
        return
    cantidad = solicitar_entero("  Cantidad inicial    : ")
    if cantidad is None:
        return
    precio = solicitar_flotante("  Precio unitario ($) : ")
    if precio is None:
        return
    categoria = input("  Categoría (Enter=General): ").strip() or "General"
    inv.agregar_producto(id_prod, nombre, cantidad, precio, categoria)


def menu_eliminar(inv: Inventario) -> None:
    print("\n  ── ELIMINAR PRODUCTO ─────────────────")
    id_prod = input("  ID del producto a eliminar: ").strip()
    confirmacion = input(f"  ¿Confirmas eliminar '{id_prod}'? (s/N): ").strip().lower()
    if confirmacion == "s":
        inv.eliminar_producto(id_prod)
    else:
        print("  Operación cancelada.")


def menu_actualizar(inv: Inventario) -> None:
    print("\n  ── ACTUALIZAR PRODUCTO ───────────────")
    id_prod = input("  ID del producto     : ").strip()
    if not inv.buscar_por_id(id_prod):
        print(f"  ✗ No existe producto con ID '{id_prod.upper()}'.")
        return
    print("  (Deja en blanco para no modificar el campo)")
    nueva_cantidad = solicitar_entero("  Nueva cantidad      : ")
    nuevo_precio   = solicitar_flotante("  Nuevo precio ($)    : ")
    if nueva_cantidad is None and nuevo_precio is None:
        print("  ✗ No se proporcionó ningún valor para actualizar.")
        return
    inv.actualizar_producto(id_prod, nueva_cantidad, nuevo_precio)


def menu_buscar(inv: Inventario) -> None:
    print("\n  ── BUSCAR PRODUCTOS ──────────────────")
    print("  1. Buscar por nombre")
    print("  2. Buscar por ID")
    print("  3. Buscar por categoría")
    opcion = input("  Opción: ").strip()

    if opcion == "1":
        termino = input("  Término de búsqueda : ").strip()
        resultados = inv.buscar_por_nombre(termino)
        if resultados:
            print(f"\n  Se encontraron {len(resultados)} resultado(s):")
            for p in resultados:
                print(f"    {p}")
        else:
            print("  Sin resultados.")

    elif opcion == "2":
        id_prod = input("  ID a buscar         : ").strip()
        producto = inv.buscar_por_id(id_prod)
        if producto:
            print(f"\n  Producto encontrado:")
            print(f"    {producto}")
            inv.mostrar_historial(id_prod)
        else:
            print("  Sin resultados.")

    elif opcion == "3":
        inv.mostrar_categorias()
        cat = input("\n  Nombre de categoría : ").strip()
        resultados = inv.buscar_por_categoria(cat)
        if resultados:
            print(f"\n  Productos en '{cat.title()}':")
            for p in resultados:
                print(f"    {p}")
        else:
            print("  Sin resultados para esa categoría.")

    else:
        print("  Opción no válida.")


def mostrar_menu_principal():
    print("\n" + "═"*50)
    print("   SISTEMA DE GESTIÓN DE INVENTARIOS")
    print("═"*50)
    print("  1. Mostrar todo el inventario")
    print("  2. Agregar producto")
    print("  3. Eliminar producto")
    print("  4. Actualizar producto")
    print("  5. Buscar producto")
    print("  6. Ver categorías")
    print("  0. Salir")
    print("─"*50)


def main():
    """Punto de entrada principal del sistema."""
    print("\n  Iniciando Sistema de Gestión de Inventarios...")
    inventario = Inventario()

    while True:
        mostrar_menu_principal()
        opcion = input("  Selecciona una opción: ").strip()

        if opcion == "1":
            inventario.mostrar_todos()
        elif opcion == "2":
            menu_agregar(inventario)
        elif opcion == "3":
            menu_eliminar(inventario)
        elif opcion == "4":
            menu_actualizar(inventario)
        elif opcion == "5":
            menu_buscar(inventario)
        elif opcion == "6":
            inventario.mostrar_categorias()
        elif opcion == "0":
            print("\n  ¡Hasta pronto! El inventario ha sido guardado.\n")
            break
        else:
            print("  ✗ Opción no válida. Intenta de nuevo.")

        pausar()


if __name__ == "__main__":
    main()