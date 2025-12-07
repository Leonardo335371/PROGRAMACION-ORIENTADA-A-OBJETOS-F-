
from abc import ABC, abstractmethod
from datetime import date

# 1. ABSTRACCIÓN
# Usamos una clase abstracta para definir un contrato que todas
# las clases hijas deberán cumplir

class Empleado(ABC):
    def __init__(self, nombre, fecha_nacimiento):

        # 2. ENCAPSULACIÓN
        # Atributos privados

        self.__nombre = nombre
        self.__fecha_nacimiento = fecha_nacimiento
        self.__salario_base = 0  # será definido por cada tipo de empleado


    @property
    def nombre(self):
        return self.__nombre

    @property
    def edad(self):
        hoy = date.today()
        return hoy.year - self.__fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.__fecha_nacimiento.month, self.__fecha_nacimiento.day)
        )

    @property
    def salario_base(self):
        return self.__salario_base

    @salario_base.setter
    def salario_base(self, valor):
        if valor < 0:
            raise ValueError("El salario no puede ser negativo")
        self.__salario_base = valor


    # Método abstracto → obliga a las clases hijas a implementarlo

    @abstractmethod
    def calcular_salario(self):
        pass

    @abstractmethod
    def trabajar(self):
        pass



# 3. HERENCIA
# Gerente y Desarrollador heredan de Empleados

class Gerente(Empleado):
    def __init__(self, nombre, fecha_nacimiento, departamento):
        super().__init__(nombre, fecha_nacimiento)
        self.departamento = departamento
        self.__bonus = 5000  # bono fijo por ser gerente

    # Sobrescritura del método abstracto
    def calcular_salario(self):
        return self.salario_base + self.__bonus

    def trabajar(self):
        return f"{self.nombre} está dirigiendo el departamento {self.departamento}"

    # Método específico de Gerente
    def reunion(self):
        return f"{self.nombre} está liderando una reunión estratégica"


class Desarrollador(Empleado):
    def __init__(self, nombre, fecha_nacimiento, lenguaje_favorito):
        super().__init__(nombre, fecha_nacimiento)
        self.lenguaje_favorito = lenguaje_favorito
        self.__horas_extra = 0

    def agregar_horas_extra(self, horas):
        if horas >= 0:
            self.__horas_extra += horas

    def calcular_salario(self):
        pago_extra = self.__horas_extra * 50
        return self.salario_base + pago_extra


    # 4. POLIMORFISMO
    # Mismo nombre de método, comportamiento diferente

    def trabajar(self):
        return f"{self.nombre} está programando en {self.lenguaje_favorito}"


class Diseñador(Empleado):
    def __init__(self, nombre, fecha_nacimiento, herramienta):
        super().__init__(nombre, fecha_nacimiento)
        self.herramienta = herramienta

    def calcular_salario(self):

        plus = 2000 if self.herramienta.lower() == "figma" else 0
        return self.salario_base + plus

    def trabajar(self):
        return f"{self.nombre} está diseñando interfaces con {self.herramienta}"



# POLIMORFISMO
# Todas las instancias son de tipo Empleado, pero llaman a su propia versión de trabajar

def jornada_laboral(empleados):
    print("=== Jornada laboral ===\n")
    for emp in empleados:
        print(emp.trabajar())
        print(f"Salario este mes: ${emp.calcular_salario():,}")
        print("-" * 40)



# USO DEL CÓDIGO

if __name__ == "__main__":
    # Crear empleados
    gerente = Gerente("Ana López", date(1985, 3, 15), "Tecnología")
    dev = Desarrollador("Carlos Ruiz", date(1992, 7, 22), "Python")
    diseñador = Diseñador("Laura Gómez", date(1990, 11, 30), "Figma")

    # Asignar salarios base
    gerente.salario_base = 30000
    dev.salario_base = 25000
    diseñador.salario_base = 22000

    # Realización de horas extra
    dev.agregar_horas_extra(20)

    # Lista de empleados
    plantilla = [gerente, dev, diseñador]

    # Ejecutar jornada laboral
    jornada_laboral(plantilla)