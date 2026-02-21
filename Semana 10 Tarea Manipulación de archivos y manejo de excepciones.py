#  Sistema de Gestión de Inventarios 


import csv
import os
import shutil
import tempfile

# Ruta del archivo donde se persiste el inventario.
# Se define como constante global para facilitar el cambio en el futuro.
ARCHIVO_INVENTARIO = "inventario.txt"

# Cabecera del CSV 
CABECERA_CSV = ["id", "nombre", "cantidad", "precio"]



# CLASE PRODUCTO  


class Producto:
    """
    Representa un producto dentro del inventario.

    Decisiones de diseño:
    - El ID se almacena como entero para facilitar comparaciones y garantizar
      unicidad numérica.
    - Se usan propiedades (@property) en lugar de métodos get/set explícitos,
      que es la convención idiomática de Python.
    - El precio y la cantidad validan que no sean negativos.
    """

    def __init__(self, id_producto: int, nombre: str, cantidad: int, precio: float):
        self.id_producto = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    # ID 
    @property
    def id_producto(self) -> int:
        return self._id_producto

    @id_producto.setter
    def id_producto(self, valor: int):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        self._id_producto = valor

    # NOMBRE 
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor

    #  CANTIDAD 
    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("La cantidad debe ser un entero no negativo.")
        self._cantidad = valor

    #  PRECIO 
    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número.")
        if valor < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = round(valor, 2)

    #  REPRESENTACIÓN 
    def __str__(self) -> str:
        return (
            f"  ID      : {self._id_producto}\n"
            f"  Nombre  : {self._nombre}\n"
            f"  Cantidad: {self._cantidad} unidades\n"
            f"  Precio  : ${self._precio:.2f}"
        )

    def __repr__(self) -> str:
        return (f"Producto(id={self._id_producto}, nombre='{self._nombre}', "
                f"cantidad={self._cantidad}, precio={self._precio})")



# FUNCIONES DE ACCESO A ARCHIVO


def _ruta_archivo() -> str:
    """Devuelve la ruta absoluta del archivo de inventario."""
    return os.path.abspath(ARCHIVO_INVENTARIO)


def guardar_inventario(productos: dict) -> tuple[bool, str]:
    """
    Escribe TODO el inventario en el archivo CSV de forma segura.

    Estrategia de escritura segura (write-then-replace):
      1. Escribe en un archivo temporal dentro del mismo directorio.
      2. Si la escritura tiene éxito, reemplaza el archivo real de forma
         atómica con shutil.move(). Esto evita corrupción parcial si el
         proceso se interrumpe a mitad de la escritura.

    Retorna (True, mensaje_ok) o (False, mensaje_error).
    """
    ruta = _ruta_archivo()
    directorio = os.path.dirname(ruta) or "."

    try:
        # Creamos el archivo temporal en el mismo directorio para que
        # shutil.move() use rename() del SO.
        fd, ruta_tmp = tempfile.mkstemp(dir=directorio, suffix=".tmp")

        try:
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CABECERA_CSV)   # Cabecera
                for p in sorted(productos.values(), key=lambda x: x.id_producto):
                    writer.writerow([p.id_producto, p.nombre, p.cantidad, p.precio])

            # Reemplazamos el archivo real con el temporal 
            shutil.move(ruta_tmp, ruta)

        except Exception:
            # Si algo falla durante la escritura eliminamos el temporal
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)
            raise   # Relanzamos para que el bloque exterior lo capture

        return True, f"Inventario guardado en '{ruta}'."

    except PermissionError:
        return False, (f"Sin permiso de escritura en '{ruta}'. "
                       "Verifique los permisos del archivo o directorio.")
    except OSError as e:
        # OSError cubre errores de disco lleno, rutas inválidas, etc.
        return False, f"Error del sistema operativo al guardar: {e}"
    except Exception as e:
        return False, f"Error inesperado al guardar el inventario: {e}"


def cargar_inventario() -> tuple[dict, list[str]]:
    """
    Lee el archivo CSV y reconstruye el diccionario de productos.

    Manejo de casos especiales:
    - Archivo inexistente → se crea uno vacío y se retorna dict vacío.
    - Cabecera faltante o incorrecta → se trata el archivo como corrupto
      y se hace una copia de seguridad antes de empezar de cero.
    - Fila con datos inválidos → se omite esa fila y se registra el error,
      permitiendo continuar con el resto de los datos válidos.
    - PermissionError → se informa al usuario y se retorna dict vacío.

    Retorna (dict_productos, lista_de_advertencias).
    """
    ruta = _ruta_archivo()
    advertencias: list[str] = []
    productos: dict[int, Producto] = {}

    #  Caso 1: El archivo no existe 
    if not os.path.exists(ruta):
        advertencias.append(
            f"Archivo '{ruta}' no encontrado. Se creará uno nuevo al guardar."
        )
        return productos, advertencias

    # Caso 2: No tenemos permiso de lectura 
    try:
        f_test = open(ruta, "r", encoding="utf-8")
        f_test.close()
    except PermissionError:
        advertencias.append(
            f"Sin permiso de lectura sobre '{ruta}'. "
            "El inventario comenzará vacío."
        )
        return productos, advertencias

    # Caso 3: Lectura normal con tolerancia a errores 
    try:
        with open(ruta, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            # Verificamos la cabecera
            try:
                cabecera = next(reader)
            except StopIteration:
                # Archivo vacío → aceptable, empieza con inventario en blanco
                return productos, advertencias

            if cabecera != CABECERA_CSV:
                # Cabecera inesperada: podría ser un archivo corrupto o de
                # otra versión. Hacemos copia de seguridad y empezamos limpio.
                ruta_bak = ruta + ".bak"
                shutil.copy2(ruta, ruta_bak)
                advertencias.append(
                    f"Cabecera de '{ruta}' no reconocida. "
                    f"Se creó copia de seguridad en '{ruta_bak}' y se "
                    "inició un inventario nuevo."
                )
                return productos, advertencias

            # Procesamos cada fila de datos
            for numero_fila, fila in enumerate(reader, start=2):
                if not fila:        # Fila completamente vacía → ignorar
                    continue
                try:
                    if len(fila) != 4:
                        raise ValueError(
                            f"Se esperaban 4 columnas, se encontraron {len(fila)}."
                        )
                    id_p     = int(fila[0])
                    nombre   = fila[1]
                    cantidad = int(fila[2])
                    precio   = float(fila[3])

                    p = Producto(id_p, nombre, cantidad, precio)

                    if id_p in productos:
                        advertencias.append(
                            f"Fila {numero_fila}: ID {id_p} duplicado; "
                            "se conserva el primero que apareció."
                        )
                    else:
                        productos[id_p] = p

                except (ValueError, IndexError) as e:
                    advertencias.append(
                        f"Fila {numero_fila} ignorada (dato inválido): {e}"
                    )

    except OSError as e:
        advertencias.append(
            f"Error del sistema operativo al leer '{ruta}': {e}. "
            "El inventario comenzará vacío."
        )
        return {}, advertencias

    return productos, advertencias



# CLASE INVENTARIO  (con persistencia en archivo)


class Inventario:
    """
    Gestiona la colección de productos de la tienda con persistencia en disco.

    Cambios respecto a v1:
    - __init__ llama a cargar_inventario() para reconstruir el estado desde
      el archivo al arrancar el programa.
    - añadir_producto, eliminar_producto y actualizar_producto llaman a
      _persistir() justo después de cada modificación exitosa.
    - _persistir() delega en guardar_inventario() y retorna el resultado
      para que la UI pueda informar al usuario.
    """

    def __init__(self):
        # Cargamos el inventario desde disco; guardamos las advertencias
        # para que main() las muestre al usuario al arrancar.
        self._productos, self.advertencias_carga = cargar_inventario()

    # PERSISTENCIA INTERNA 

    def _persistir(self) -> tuple[bool, str]:
        """
        Guarda el estado actual en disco.
        Retorna (éxito, mensaje) para informar a la UI.
        """
        return guardar_inventario(self._productos)

    # AÑADIR 

    def añadir_producto(self, producto: Producto) -> tuple[bool, str]:
        """
        Añade un producto y persiste el inventario.
        Retorna (True, msg_ok) o (False, msg_error).
        """
        if producto.id_producto in self._productos:
            return False, f"ID {producto.id_producto} ya existe en el inventario."

        self._productos[producto.id_producto] = producto
        ok, msg = self._persistir()
        if ok:
            return True, f"Producto '{producto.nombre}' añadido y guardado con éxito."
        else:
            # Revertimos el cambio en memoria si no se pudo guardar
            del self._productos[producto.id_producto]
            return False, f"No se pudo guardar el inventario: {msg}"

    #  ELIMINAR 

    def eliminar_producto(self, id_producto: int) -> tuple[bool, str]:
        """
        Elimina un producto y persiste el inventario.
        Retorna (True, msg_ok) o (False, msg_error).
        """
        if id_producto not in self._productos:
            return False, f"No existe ningún producto con ID {id_producto}."

        # Guardamos copia para poder revertir si falla el guardado
        producto_backup = self._productos.pop(id_producto)
        ok, msg = self._persistir()
        if ok:
            return True, f"Producto con ID {id_producto} eliminado y guardado con éxito."
        else:
            # Revertimos
            self._productos[id_producto] = producto_backup
            return False, f"No se pudo guardar el inventario: {msg}"

    #  ACTUALIZAR 

    def actualizar_producto(
        self,
        id_producto: int,
        nueva_cantidad: int | None = None,
        nuevo_precio: float | None = None
    ) -> tuple[bool, str]:
        """
        Actualiza cantidad y/o precio, luego persiste.
        Retorna (True, msg_ok) o (False, msg_error).
        """
        if id_producto not in self._productos:
            return False, f"No existe ningún producto con ID {id_producto}."

        producto = self._productos[id_producto]

        # Guardamos valores anteriores para poder revertir
        cantidad_anterior = producto.cantidad
        precio_anterior   = producto.precio

        if nueva_cantidad is not None:
            producto.cantidad = nueva_cantidad
        if nuevo_precio is not None:
            producto.precio = nuevo_precio

        ok, msg = self._persistir()
        if ok:
            return True, "Producto actualizado y guardado con éxito."
        else:
            # Revertimos los valores en memoria
            producto.cantidad = cantidad_anterior
            producto.precio   = precio_anterior
            return False, f"No se pudo guardar el inventario: {msg}"

    #  CONSULTAS 

    def buscar_por_nombre(self, nombre: str) -> list[Producto]:
        termino = nombre.strip().lower()
        return [p for p in self._productos.values()
                if termino in p.nombre.lower()]

    def mostrar_todos(self) -> list[Producto]:
        return sorted(self._productos.values(), key=lambda p: p.id_producto)

    def esta_vacio(self) -> bool:
        return len(self._productos) == 0

    def id_existe(self, id_producto: int) -> bool:
        return id_producto in self._productos

    def siguiente_id(self) -> int:
        if self.esta_vacio():
            return 1
        return max(self._productos.keys()) + 1



# INTERFAZ DE USUARIO EN CONSOLA


LINEA     = "=" * 55
SEPARADOR = "-" * 55


def limpiar_pantalla():
    print("\n" * 2)


def pausar():
    input("\n  Presione Enter para continuar...")


def encabezado(titulo: str):
    print(f"\n{LINEA}")
    print(f"  {titulo}")
    print(LINEA)


def _mostrar_resultado(ok: bool, mensaje: str):
    """
    Muestra el resultado de una operación de forma uniforme.
    ✔ para éxito, ✗ para fallo.
    """
    icono = "✔" if ok else "✗"
    print(f"\n  {icono} {mensaje}")


#  Funciones de entrada segura 

def pedir_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠ Ingrese un valor mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠ Ingrese un valor menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠ Entrada inválida. Ingrese un número entero.")


def pedir_flotante(mensaje: str, minimo: float = 0.0) -> float:
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
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  ⚠ Este campo no puede estar vacío.")


#  Operaciones del menú 

def op_añadir(inventario: Inventario):
    """Flujo completo para añadir un nuevo producto."""
    encabezado("AÑADIR PRODUCTO")
    print(f"  (Próximo ID sugerido: {inventario.siguiente_id()})")

    id_p = pedir_entero("  ID del producto   : ", minimo=1)

    if inventario.id_existe(id_p):
        _mostrar_resultado(False, f"Ya existe un producto con ID {id_p}. Operación cancelada.")
        pausar()
        return

    nombre   = pedir_texto("  Nombre            : ")
    cantidad = pedir_entero("  Cantidad inicial  : ", minimo=0)
    precio   = pedir_flotante("  Precio unitario   : $", minimo=0.0)

    try:
        nuevo = Producto(id_p, nombre, cantidad, precio)
        ok, msg = inventario.añadir_producto(nuevo)
        _mostrar_resultado(ok, msg)
    except ValueError as e:
        _mostrar_resultado(False, f"Error al crear producto: {e}")

    pausar()


def op_eliminar(inventario: Inventario):
    """Flujo para eliminar un producto por ID con confirmación."""
    encabezado("ELIMINAR PRODUCTO")

    if inventario.esta_vacio():
        print("  El inventario está vacío. No hay productos para eliminar.")
        pausar()
        return

    id_p = pedir_entero("  ID del producto a eliminar: ", minimo=1)

    resultados = [p for p in inventario.mostrar_todos() if p.id_producto == id_p]
    if not resultados:
        _mostrar_resultado(False, f"No se encontró ningún producto con ID {id_p}.")
        pausar()
        return

    print(f"\n  Producto encontrado:\n{resultados[0]}")
    confirmar = input("\n  ¿Confirma la eliminación? (s/n): ").strip().lower()

    if confirmar == "s":
        ok, msg = inventario.eliminar_producto(id_p)
        _mostrar_resultado(ok, msg)
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
        _mostrar_resultado(False, f"No se encontró ningún producto con ID {id_p}.")
        pausar()
        return

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
        ok, msg = inventario.actualizar_producto(id_p, nueva_cantidad, nuevo_precio)
        _mostrar_resultado(ok, msg)

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
        _mostrar_resultado(False, f"No se encontraron productos que contengan '{termino}'.")
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
    print(f"  Archivo: {_ruta_archivo()}\n")

    for p in productos:
        print(p)
        print(f"  {SEPARADOR}")

    pausar()


def mostrar_menu():
    print(f"\n{LINEA}")
    print("       SISTEMA DE GESTIÓN DE INVENTARIOS  v2.0")
    print(LINEA)
    print("  1. Añadir producto")
    print("  2. Eliminar producto")
    print("  3. Actualizar cantidad / precio")
    print("  4. Buscar producto por nombre")
    print("  5. Mostrar todos los productos")
    print("  0. Salir")
    print(LINEA)



# PUNTO DE ENTRADA


def main():
    """
    Función principal.

    Al iniciar:
      1. Se carga el inventario desde inventario.txt (si existe).
      2. Se muestran las advertencias de carga (filas corruptas, etc.).
      3. Si el archivo está vacío/inexistente se ofrecen datos de ejemplo.

    Al salir:
      El inventario ya está persistido porque cada operación guarda
      inmediatamente; no se necesita un guardado final explícito.
    """
    print(f"\n{LINEA}")
    print("  SISTEMA DE GESTIÓN DE INVENTARIOS  v2.0")
    print(f"{LINEA}")
    print(f"  Cargando inventario desde '{ARCHIVO_INVENTARIO}'...")

    inventario = Inventario()

    # Mostramos advertencias de carga 
    if inventario.advertencias_carga:
        print(f"\n  ⚠ Advertencias durante la carga:")
        for adv in inventario.advertencias_carga:
            print(f"    · {adv}")

    # Informamos cuántos productos se cargaron
    n = len(inventario.mostrar_todos())
    if n > 0:
        print(f"\n  ✔ Se cargaron {n} producto(s) desde el archivo.")
    else:
        print("\n  El archivo está vacío o no existe aún.")
        # Si no hay datos, ofrecemos cargar ejemplos
        cargar_ej = input(
            "  ¿Desea cargar productos de ejemplo? (s/n): "
        ).strip().lower()
        if cargar_ej == "s":
            datos_ejemplo = [
                Producto(1, "Manzana Roja",   100, 0.50),
                Producto(2, "Manzana Verde",   80, 0.55),
                Producto(3, "Leche Entera",    50, 1.20),
                Producto(4, "Pan Integral",    30, 2.50),
                Producto(5, "Jugo de Naranja", 20, 3.75),
            ]
            for p in datos_ejemplo:
                ok, msg = inventario.añadir_producto(p)
                if not ok:
                    print(f"  ✗ No se pudo añadir '{p.nombre}': {msg}")
            print(f"  ✔ Se cargaron {len(datos_ejemplo)} productos de ejemplo.")

    #  Ciclo principal del menú 
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
            print("  ⚠ Opción no válida. Ingrese un número del 0 al 5.")


if __name__ == "__main__":
    main()