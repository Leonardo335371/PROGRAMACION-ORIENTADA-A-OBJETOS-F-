# Clase base para representar un Pproducto en la tienda.
class Producto:
    def __init__(self, nombre, precio, stock):
        # Atributos: nombre del producto, precio y cantidad en stock.
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def mostrar_info(self):
        # Método para mostrar la información del producto.
        return f"Producto: {self.nombre}, Precio: ${self.precio:.2f}, Stock: {self.stock}"

    def reducir_stock(self, cantidad):
        # Método para reducir el stock cuando se agrega al carrito.
        # Verifica si hay producto disponible.
        if cantidad <= self.stock:
            self.stock -= cantidad
            return True
        else:
            print(f"No hay suficiente stock para {self.nombre}.")
            return False

# Clase para representar el Carrito de compra.
class Carrito:
    def __init__(self):
        # Atributo: diccionario para almacenar productos y sus cantidades.
        self.items = {}  # clave: producto, valor: cantidad

    def agregar_producto(self, producto, cantidad):
        # Método para agregar un producto al carrito.
        # Interactúa con el método reducir_stock del producto.
        if producto.reducir_stock(cantidad):
            if producto in self.items:
                self.items[producto] += cantidad
            else:
                self.items[producto] = cantidad
            print(f"Se agregaron {cantidad} unidades de {producto.nombre} al carrito.")
        else:
            print("No se pudo agregar el producto.")

    def calcular_total(self):
        # Método para calcular el total del carrito.
        total = 0
        for producto, cantidad in self.items.items():
            total += producto.precio * cantidad
        return total

    def mostrar_carrito(self):
        # Método para mostrar el contenido del carrito.
        if not self.items:
            return "El carrito está vacío."
        info = "Contenido del carrito:\n"
        for producto, cantidad in self.items.items():
            info += f"- {producto.nombre}: {cantidad} unidades, Subtotal: ${producto.precio * cantidad:.2f}\n"
        info += f"Total: ${self.calcular_total():.2f}"
        return info

# Clase para representar un Cliente.
class Cliente:
    def __init__(self, nombre, email):
        # Atributos: nombre del cliente, email y su carrito asociado.
        self.nombre = nombre
        self.email = email
        self.carrito = Carrito()  # Cada cliente tiene su propio carrito.

    def agregar_al_carrito(self, producto, cantidad):
        # Método que delega la adición al carrito del cliente.
        self.carrito.agregar_producto(producto, cantidad)

    def realizar_compra(self):
        # Método para finalizar la compra.
        # Muestra el carrito y calcula el total.
        print(f"Cliente: {self.nombre}")
        print(self.carrito.mostrar_carrito())
        total = self.carrito.calcular_total()
        if total > 0:
            print(f"Compra realizada por {self.email}. Total pagado: ${total:.2f}")
            self.carrito.items.clear()  # Vacía el carrito después de la compra.
        else:
            print("No hay items para comprar.")

# Ejemplo de uso
# Productos.
producto1 = Producto("Laptop", 1200.00, 5)
producto2 = Producto("Mouse", 25.00, 10)

# Cliente.
cliente = Cliente("Leonardo Capella", "LeonardoCa@gmail.com")

# Agregar productos al carrito del cliente.
cliente.agregar_al_carrito(producto1, 1)
cliente.agregar_al_carrito(producto2, 2)

# Realizar la compra.
cliente.realizar_compra()

# Mostrar info de un producto después de la interacción.
print(producto1.mostrar_info())