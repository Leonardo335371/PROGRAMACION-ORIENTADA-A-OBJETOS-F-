"""
Sistema de Gestión de Biblioteca Digital
Implementa la gestión de libros, usuarios, categorías e historial de préstamos
utilizando las estructuras de datos apropiadas de Python.
"""

from datetime import datetime
from typing import Optional


# CLASE LIBRO

class Libro:
    """
    Representa un libro en la biblioteca digital.

    Decisión de diseño:
    - 'info' es una TUPLA (autor, título) porque estos datos son INMUTABLES
      una vez que el libro es creado. Las tuplas comunican esta intención.
    - El resto de atributos (categoría, disponible) sí pueden cambiar.
    """

    def __init__(self, isbn: str, titulo: str, autor: str,
                 categoria: str, anio: int = None):
        self.isbn = isbn                      # Identificador único del libro
        self.info = (autor, titulo)           # TUPLA inmutable: (autor, título)
        self.categoria = categoria            # Puede actualizarse si es necesario
        self.anio = anio                      # Año de publicación
        self.disponible = True                # True = en estantería, False = prestado

    @property
    def titulo(self) -> str:
        """Acceso cómodo al título desde la tupla inmutable."""
        return self.info[1]

    @property
    def autor(self) -> str:
        """Acceso cómodo al autor desde la tupla inmutable."""
        return self.info[0]

    def __repr__(self) -> str:
        estado = "✅ Disponible" if self.disponible else "📤 Prestado"
        return (f"Libro(ISBN={self.isbn}, Título='{self.titulo}', "
                f"Autor='{self.autor}', Categoría='{self.categoria}', "
                f"Estado={estado})")

    def __str__(self) -> str:
        estado = "Disponible" if self.disponible else "Prestado"
        return f"'{self.titulo}' de {self.autor} [{self.categoria}] — {estado}"


# CLASE USUARIO

class Usuario:
    """
    Representa a un usuario registrado en la biblioteca.

    Decisión de diseño:
    - 'libros_prestados' es una LISTA porque los préstamos son ordenados
      y pueden haber múltiples entradas del mismo tipo (aunque no del mismo ISBN).
    - La lista permite agregar y quitar con facilidad.
    """

    def __init__(self, usuario_id: str, nombre: str, email: str = ""):
        self.usuario_id = usuario_id          # ID único del usuario
        self.nombre = nombre                  # Nombre completo
        self.email = email                    # Correo electrónico (opcional)
        self.libros_prestados: list[str] = [] # LISTA de ISBNs actualmente prestados
        self.fecha_registro = datetime.now()  # Fecha de alta en el sistema

    def tiene_libro(self, isbn: str) -> bool:
        """Verifica si el usuario tiene actualmente prestado un libro."""
        return isbn in self.libros_prestados

    def agregar_prestamo(self, isbn: str) -> None:
        """Registra un nuevo préstamo en la lista del usuario."""
        self.libros_prestados.append(isbn)

    def quitar_prestamo(self, isbn: str) -> bool:
        """
        Elimina un préstamo de la lista.
        Retorna True si se eliminó, False si no existía.
        """
        if isbn in self.libros_prestados:
            self.libros_prestados.remove(isbn)
            return True
        return False

    def total_prestamos(self) -> int:
        """Retorna cuántos libros tiene actualmente el usuario."""
        return len(self.libros_prestados)

    def __repr__(self) -> str:
        return (f"Usuario(ID={self.usuario_id}, Nombre='{self.nombre}', "
                f"Préstamos actuales={self.total_prestamos()})")

    def __str__(self) -> str:
        return f"{self.nombre} (ID: {self.usuario_id}) — {self.total_prestamos()} libro(s) prestado(s)"


# CLASE REGISTRO DE PRÉSTAMO 

class RegistroPrestamo:
    """
    Registro inmutable de un evento de préstamo o devolución.
    Sirve como entrada en el historial de la biblioteca.
    """

    def __init__(self, usuario_id: str, isbn: str, tipo: str):
        # Usamos tupla para los datos clave del registro: son inmutables
        self.datos = (usuario_id, isbn, tipo, datetime.now())

    @property
    def usuario_id(self): return self.datos[0]

    @property
    def isbn(self): return self.datos[1]

    @property
    def tipo(self): return self.datos[2]  

    @property
    def fecha(self): return self.datos[3]

    def __str__(self) -> str:
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M")
        return f"[{fecha_str}] {self.tipo} — Usuario {self.usuario_id} / ISBN {self.isbn}"


# CLASE BIBLIOTECA

class Biblioteca:
    """
    Gestiona la colección completa: libros, usuarios y préstamos.

    Decisiones de diseño:
    - 'catalogo': DICCIONARIO {ISBN -> Libro} para búsquedas O(1) por ISBN.
    - 'ids_usuarios': CONJUNTO (set) para garantizar unicidad de IDs y
      verificación O(1) de existencia.
    - 'usuarios': DICCIONARIO {ID -> Usuario} para acceso directo al objeto.
    - 'historial': LISTA de RegistroPrestamo, ordenada cronológicamente.
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        # DICCIONARIO: ISBN -> objeto Libro (acceso eficiente por ISBN)
        self.catalogo: dict[str, Libro] = {}
        # CONJUNTO: IDs únicos de usuarios registrados
        self.ids_usuarios: set[str] = set()
        # DICCIONARIO: usuario_id -> objeto Usuario
        self.usuarios: dict[str, Usuario] = {}
        # LISTA: historial cronológico de todos los préstamos/devoluciones
        self.historial: list[RegistroPrestamo] = []

    # GESTIÓN DE LIBROS

    def añadir_libro(self, libro: Libro) -> bool:
        """
        Añade un libro al catálogo.
        Retorna False si el ISBN ya existe.
        """
        if libro.isbn in self.catalogo:
            print(f"⚠️  Ya existe un libro con ISBN {libro.isbn}.")
            return False
        self.catalogo[libro.isbn] = libro
        print(f"✅ Libro añadido: {libro}")
        return True

    def quitar_libro(self, isbn: str) -> Optional[Libro]:
        """
        Quita un libro del catálogo por ISBN.
        No permite quitar un libro que esté prestado actualmente.
        Retorna el libro eliminado o None.
        """
        if isbn not in self.catalogo:
            print(f"⚠️  No se encontró libro con ISBN {isbn}.")
            return None
        libro = self.catalogo[isbn]
        if not libro.disponible:
            print(f"⚠️  No se puede quitar '{libro.titulo}': está prestado.")
            return None
        # Eliminamos del diccionario usando del
        del self.catalogo[isbn]
        print(f"🗑️  Libro eliminado: {libro}")
        return libro

    # GESTIÓN DE USUARIOS

    def registrar_usuario(self, usuario: Usuario) -> bool:
        """
        Registra un nuevo usuario.
        El conjunto 'ids_usuarios' garantiza que no haya IDs duplicados.
        """
        if usuario.usuario_id in self.ids_usuarios:
            print(f"⚠️  El ID de usuario '{usuario.usuario_id}' ya existe.")
            return False
        # Añadimos al conjunto 
        self.ids_usuarios.add(usuario.usuario_id)
        # Añadimos al diccionario para acceso por ID
        self.usuarios[usuario.usuario_id] = usuario
        print(f"✅ Usuario registrado: {usuario}")
        return True

    def dar_de_baja(self, usuario_id: str) -> Optional[Usuario]:
        """
        Da de baja a un usuario.
        No permite dar de baja a alguien con préstamos activos.
        """
        if usuario_id not in self.ids_usuarios:
            print(f"⚠️  No se encontró el usuario '{usuario_id}'.")
            return None
        usuario = self.usuarios[usuario_id]
        if usuario.total_prestamos() > 0:
            print(f"⚠️  {usuario.nombre} tiene {usuario.total_prestamos()} libro(s) pendiente(s) de devolver.")
            return None
        # Eliminamos del conjunto y del diccionario
        self.ids_usuarios.discard(usuario_id)
        del self.usuarios[usuario_id]
        print(f"🗑️  Usuario dado de baja: {usuario.nombre}")
        return usuario

    # PRÉSTAMOS Y DEVOLUCIONES

    def prestar_libro(self, usuario_id: str, isbn: str) -> bool:
        """
        Presta un libro disponible a un usuario registrado.
        Registra el evento en el historial.
        """
        # Verificamos que el usuario existe (búsqueda O(1) en el conjunto)
        if usuario_id not in self.ids_usuarios:
            print(f"⚠️  Usuario '{usuario_id}' no encontrado.")
            return False
        # Verificamos que el libro existe (búsqueda O(1) en el diccionario)
        if isbn not in self.catalogo:
            print(f"⚠️  Libro con ISBN '{isbn}' no encontrado.")
            return False

        libro = self.catalogo[isbn]
        usuario = self.usuarios[usuario_id]

        if not libro.disponible:
            print(f"⚠️  '{libro.titulo}' no está disponible actualmente.")
            return False
        if usuario.tiene_libro(isbn):
            print(f"⚠️  {usuario.nombre} ya tiene prestado ese libro.")
            return False

        # Realizamos el préstamo
        libro.disponible = False
        usuario.agregar_prestamo(isbn)

        # Registramos en el historial
        self.historial.append(RegistroPrestamo(usuario_id, isbn, "PRÉSTAMO"))

        print(f"📤 Préstamo realizado: '{libro.titulo}' → {usuario.nombre}")
        return True

    def devolver_libro(self, usuario_id: str, isbn: str) -> bool:
        """
        Registra la devolución de un libro.
        """
        if usuario_id not in self.ids_usuarios:
            print(f"⚠️  Usuario '{usuario_id}' no encontrado.")
            return False
        if isbn not in self.catalogo:
            print(f"⚠️  Libro con ISBN '{isbn}' no encontrado.")
            return False

        usuario = self.usuarios[usuario_id]
        libro = self.catalogo[isbn]

        if not usuario.tiene_libro(isbn):
            print(f"⚠️  {usuario.nombre} no tiene prestado el libro '{libro.titulo}'.")
            return False

        # Realizamos la devolución
        libro.disponible = True
        usuario.quitar_prestamo(isbn)

        # Registramos en el historial
        self.historial.append(RegistroPrestamo(usuario_id, isbn, "DEVOLUCIÓN"))

        print(f"📥 Devolución registrada: '{libro.titulo}' ← {usuario.nombre}")
        return True

    # BÚSQUEDAS

    def buscar_por_titulo(self, termino: str) -> list[Libro]:
        """Busca libros cuyo título contenga el término (sin distinción de mayúsculas)."""
        termino = termino.lower()
        # Comprensión de lista sobre los valores del diccionario
        return [libro for libro in self.catalogo.values()
                if termino in libro.titulo.lower()]

    def buscar_por_autor(self, termino: str) -> list[Libro]:
        """Busca libros por nombre de autor."""
        termino = termino.lower()
        return [libro for libro in self.catalogo.values()
                if termino in libro.autor.lower()]

    def buscar_por_categoria(self, categoria: str) -> list[Libro]:
        """Devuelve todos los libros de una categoría dada."""
        categoria = categoria.lower()
        return [libro for libro in self.catalogo.values()
                if libro.categoria.lower() == categoria]

    def buscar_disponibles(self) -> list[Libro]:
        """Retorna solo los libros actualmente disponibles."""
        return [libro for libro in self.catalogo.values() if libro.disponible]

    # LISTADOS

    def listar_libros_prestados(self, usuario_id: str) -> list[Libro]:
        """
        Muestra todos los libros que tiene prestados un usuario.
        """
        if usuario_id not in self.ids_usuarios:
            print(f"⚠️  Usuario '{usuario_id}' no encontrado.")
            return []
        usuario = self.usuarios[usuario_id]
        prestados = [self.catalogo[isbn] for isbn in usuario.libros_prestados
                     if isbn in self.catalogo]
        if not prestados:
            print(f"ℹ️  {usuario.nombre} no tiene libros prestados.")
        else:
            print(f"\n📚 Libros prestados a {usuario.nombre}:")
            for libro in prestados:
                print(f"   • {libro}")
        return prestados

    def mostrar_historial(self, limite: int = 10) -> None:
        """Muestra los últimos N registros del historial."""
        print(f"\n📋 Historial de préstamos (últimos {limite}):")
        for registro in self.historial[-limite:]:
            print(f"   {registro}")

    def estadisticas(self) -> dict:
        """Retorna un resumen estadístico de la biblioteca."""
        total = len(self.catalogo)
        disponibles = sum(1 for l in self.catalogo.values() if l.disponible)
        prestados = total - disponibles
        # Conjunto de categorías únicas
        categorias = {l.categoria for l in self.catalogo.values()}

        return {
            "total_libros": total,
            "disponibles": disponibles,
            "prestados": prestados,
            "total_usuarios": len(self.ids_usuarios),
            "categorias": categorias,
            "total_transacciones": len(self.historial),
        }

    def __str__(self) -> str:
        stats = self.estadisticas()
        return (f"Biblioteca '{self.nombre}' — "
                f"{stats['total_libros']} libros, "
                f"{stats['total_usuarios']} usuarios, "
                f"{stats['prestados']} préstamo(s) activo(s)")


# DEMOSTRACIÓN DEL SISTEMA

if __name__ == "__main__":
    print("=" * 60)
    print("  SISTEMA DE GESTIÓN DE BIBLIOTECA DIGITAL")
    print("=" * 60)

    # Crear biblioteca
    bib = Biblioteca("BiblioTech Central")

    # Añadir libros
    print("\n📖 AÑADIENDO LIBROS AL CATÁLOGO")
    print("-" * 40)
    libros = [
        Libro("978-0-7432-7356-5", "1984", "George Orwell", "Distopía", 1949),
        Libro("978-0-06-112008-4", "To Kill a Mockingbird", "Harper Lee", "Ficción", 1960),
        Libro("978-0-7432-7357-2", "Brave New World", "Aldous Huxley", "Distopía", 1932),
        Libro("978-0-14-028329-7", "El Alquimista", "Paulo Coelho", "Autoayuda", 1988),
        Libro("978-84-339-5000-4", "Cien Años de Soledad", "Gabriel García Márquez", "Realismo Mágico", 1967),
        Libro("978-0-7432-7358-9", "Fahrenheit 451", "Ray Bradbury", "Distopía", 1953),
        Libro("978-0-14-044913-6", "Don Quijote", "Miguel de Cervantes", "Clásico", 1605),
        Libro("978-0-06-093546-9", "El Gran Gatsby", "F. Scott Fitzgerald", "Ficción", 1925),
    ]
    for libro in libros:
        bib.añadir_libro(libro)

    # Registrar usuarios
    print("\n👥 REGISTRANDO USUARIOS")
    print("-" * 40)
    usuarios = [
        Usuario("U001", "Ana García", "ana@email.com"),
        Usuario("U002", "Carlos López", "carlos@email.com"),
        Usuario("U003", "María Fernández", "maria@email.com"),
    ]
    for usuario in usuarios:
        bib.registrar_usuario(usuario)

    # Intentar registrar usuario duplicado
    bib.registrar_usuario(Usuario("U001", "Duplicado", "dup@email.com"))

    # Prestar libros 
    print("\n📤 PRÉSTAMOS")
    print("-" * 40)
    bib.prestar_libro("U001", "978-0-7432-7356-5")   # Ana pide 1984
    bib.prestar_libro("U001", "978-84-339-5000-4")   # Ana pide Cien Años
    bib.prestar_libro("U002", "978-0-7432-7357-2")   # Carlos pide Brave New World
    bib.prestar_libro("U003", "978-0-14-028329-7")   # María pide El Alquimista
    bib.prestar_libro("U002", "978-0-7432-7356-5")   # Error: ya prestado

    # Listar libros prestados
    print("\n📋 LIBROS POR USUARIO")
    print("-" * 40)
    bib.listar_libros_prestados("U001")
    bib.listar_libros_prestados("U002")

    # Búsquedas
    print("\n🔍 BÚSQUEDAS")
    print("-" * 40)

    print("\nBúsqueda por título: '1984'")
    resultados = bib.buscar_por_titulo("1984")
    for r in resultados:
        print(f"  → {r}")

    print("\nBúsqueda por autor: 'Orwell'")
    resultados = bib.buscar_por_autor("Orwell")
    for r in resultados:
        print(f"  → {r}")

    print("\nBúsqueda por categoría: 'Distopía'")
    resultados = bib.buscar_por_categoria("Distopía")
    for r in resultados:
        print(f"  → {r}")

    print("\nLibros disponibles:")
    for r in bib.buscar_disponibles():
        print(f"  → {r}")

    # Devoluciones
    print("\n📥 DEVOLUCIONES")
    print("-" * 40)
    bib.devolver_libro("U001", "978-0-7432-7356-5")  # Ana devuelve 1984
    bib.devolver_libro("U002", "978-0-7432-7357-2")  # Carlos devuelve Brave New World

    # Historial 
    bib.mostrar_historial(limite=8)

    # Estadísticas finales
    print("\n📊 ESTADÍSTICAS FINALES")
    print("-" * 40)
    stats = bib.estadisticas()
    print(f"  Total de libros:       {stats['total_libros']}")
    print(f"  Libros disponibles:    {stats['disponibles']}")
    print(f"  Libros prestados:      {stats['prestados']}")
    print(f"  Usuarios registrados:  {stats['total_usuarios']}")
    print(f"  Categorías únicas:     {stats['categorias']}")
    print(f"  Total transacciones:   {stats['total_transacciones']}")
    print(f"\n  {bib}")
    print("\n" + "=" * 60)