class Vehiculo:
    """
    Clase base que representa un vehículo.
    Demuestra encapsulación con atributos privados.
    """
    def __init__(self, marca, modelo, año):
        self._marca = marca  # Atributo encapsulado
        self._modelo = modelo  # Atributo encapsulado
        self._año = año  # Atributo encapsulado
        self.velocidad = 0  # Atributo público

    def acelerar(self, incremento):
        """Método para aumentar la velocidad."""
        self.velocidad += incremento
        print(f"El vehículo acelera a {self.velocidad} km/h.")

    def frenar(self):
        """Método para detener el vehículo."""
        self.velocidad = 0
        print("El vehículo se ha detenido.")

    def describir(self):
        """Método para describir el vehículo. Será sobrescrito en la clase derivada (polimorfismo)."""
        return f"Vehículo: {self._marca} {self._modelo} del año {self._año}"

    def info_adicional(self, *args):

        if args:
            print("Información adicional:")
            for arg in args:
                print(f"- {arg}")
        else:
            print("No hay información adicional.")

class Coche(Vehiculo):
    """
    Clase derivada que hereda de Vehiculo.
    Accede a atributos y métodos de la clase base.
    """
    def __init__(self, marca, modelo, año, puertas):
        super().__init__(marca, modelo, año)  # Llamada al constructor de la clase base
        self.puertas = puertas  # Atributo adicional específico de Coche

    def describir(self):
        # Accede a atributos encapsulados de la clase base
        return f"Coche: {self._marca} {self._modelo} del año {self._año} con {self.puertas} puertas"

# Creación de instancias para demostrar la funcionalidad
vehiculo_generico = Vehiculo("Genérico", "ModeloX", 2020)
coche_especifico = Coche("Toyota", "Corolla", 2022, 4)

# Demostración de métodos y conceptos
print("Demostración de Vehiculo base:")
print(vehiculo_generico.describir())  # Llama al método original
vehiculo_generico.acelerar(50)
vehiculo_generico.frenar()
vehiculo_generico.info_adicional("Color: Naranja", "Kilometraje: 10000 km")  # Polimorfismo con args variables

print("\nDemostración del Coche:")
print(coche_especifico.describir())  # Llama al método sobrescrito
coche_especifico.acelerar(80)  # Método heredado
coche_especifico.info_adicional()  # Método heredado con args variables
coche_especifico.frenar()  # Método heredado
