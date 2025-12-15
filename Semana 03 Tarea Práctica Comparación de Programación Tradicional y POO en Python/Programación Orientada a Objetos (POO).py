# Programación Orientada a Objetos (POO): Cálculo del promedio semanal de temperaturas


class DailyWeather:
    """
    Clase que representa la información diaria del clima.
    - Encapsula las temperaturas (mañana, tarde, noche) y el promedio diario.
    - Métodos para ingresar datos y calcular/ obtener el promedio (encapsulamiento: datos privados).
    """

    def __init__(self, day):
        """
        Inicializador: Recibe el nombre del día y inicializa temperaturas como lista vacía.
        El promedio se calcula solo cuando se necesita (lazy computation).
        """
        self.day = day  # Atributo público: nombre del día
        self._temperatures = []  # Atributo privado: lista de temperaturas
        self._daily_average = None  # Atributo privado: promedio diario

    def input_temperatures(self):
        """
        Método para ingresar las 3 temperaturas del día.
        - Solicita inputs al usuario con validación de números.
        - Almacena en el atributo privado _temperatures.
        - Resetea el promedio para recalcular si es necesario.
        """
        print(f"Ingresando temperaturas para el {self.day}:")
        self._temperatures = []  # Limpiar por si se llama múltiples veces
        for momento in ["mañana", "tarde", "noche"]:
            while True:
                try:
                    temp = float(input(f"Temperatura de la {momento} (en °C): "))
                    self._temperatures.append(temp)
                    break
                except ValueError:
                    print("Por favor, ingrese un valor numérico válido.")
        self._daily_average = None
        print(f"Temperaturas ingresadas para {self.day}: {self._temperatures}\n")

    def calculate_daily_average(self):
        """
        Método para calcular el promedio diario si no está calculado.
        - Usa las temperaturas privadas.
        - Almacena en _daily_average para evitar recalculos innecesarios (memoization simple).
        - Retorna el promedio.
        """
        if not self._temperatures:
            raise ValueError(f"No hay temperaturas ingresadas para {self.day}")
        if self._daily_average is None:
            self._daily_average = sum(self._temperatures) / len(self._temperatures)
        return self._daily_average

    def get_daily_average(self):
        """
        Getter para obtener el promedio diario (encapsulamiento: no acceso directo a _daily_average).
        - Asegura que se calcule si no está hecho.
        """
        return self.calculate_daily_average()


class WeeklyWeather:
    """
    Clase que representa la información semanal del clima.
    - Usa composición: Contiene una lista de objetos DailyWeather.
    - Métodos para ingresar datos de toda la semana y calcular el promedio semanal.
    - Encapsulamiento: La lista de días es privada.
    """

    def __init__(self):
        """
        Inicializador: Crea la lista de días de la semana y objetos DailyWeather correspondientes.
        """
        self._days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self._daily_weathers = [DailyWeather(day) for day in self._days]

    def input_all_days(self):
        """
        Método para ingresar datos para todos los días de la semana.
        - Llama al método input_temperatures() de cada DailyWeather.
        """
        print("=== Ingreso de Datos Semanales de Temperaturas ===\n")
        for daily in self._daily_weathers:
            daily.input_temperatures()

    def calculate_weekly_average(self):
        """
        Método para calcular el promedio semanal.
        - Obtiene los promedios diarios de cada DailyWeather (usando sus métodos).
        - Calcula y retorna el promedio de esos promedios.
        - Muestra un resumen detallado.
        """
        daily_averages = []
        for daily in self._daily_weathers:
            avg = daily.get_daily_average()
            daily_averages.append(avg)

        weekly_average = sum(daily_averages) / len(daily_averages)

        # Mostrar resumen
        print("=== Resumen Semanal ===")
        for i, daily in enumerate(self._daily_weathers):
            print(f"{daily.day}: {daily_averages[i]:.2f} °C")
        print(f"\nPromedio semanal: {weekly_average:.2f} °C")

        return weekly_average


# Ejecución del programa
if __name__ == "__main__":
    week = WeeklyWeather()
    week.input_all_days()
    week.calculate_weekly_average()