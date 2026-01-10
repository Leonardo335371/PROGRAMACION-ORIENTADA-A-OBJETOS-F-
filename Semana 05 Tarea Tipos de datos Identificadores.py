
def convertir_centimetros_a_pulgadas(centimetros: float) -> float:
    """Convierte centímetros a pulgadas (1 cm = 0.393701 pulgadas)"""
    return centimetros * 0.393701


def convertir_celsius_a_fahrenheit(celsius: float) -> float:
    """Convierte temperatura de Celsius a Fahrenheit"""
    return (celsius * 9 / 5) + 32


def main():
    #Tipos de Datos
    nombre_usuario = "Leonardo"
    edad = 18
    estatura_cm = 170
    es_estudiante = True
    print("")
    print("BIENVENIDO")
    print("\n")

    print(f"Hola {nombre_usuario}!")
    print(f"Tienes {edad} años y mides {estatura_cm} cm")
    print(f"¿Eres estudiante? → {'Sí' if es_estudiante else 'No'}\n")

    #Converción de Distancia
    print("=== Conversor de Centímetros a Pulgadas ===")
    while True:
        try:
            valor_cm = float(input("Ingresa una longitud en centímetros (0 para salir): "))

            if valor_cm == 0:
                print("¡Gracias por usar el conversor de distancia!\n")
                break

            pulgadas = convertir_centimetros_a_pulgadas(valor_cm)
            print(f"{valor_cm:6.1f} cm  →  {pulgadas:6.2f} pulgadas\n")

        except ValueError:
            print("¡Por favor ingresa un número válido!\n")

    #Converción de Temperatura
    print("\n=== Conversor de Celsius a Fahrenheit ===")
    temp_c = float(input("Temperatura en °C: "))
    temp_f = convertir_celsius_a_fahrenheit(temp_c)

    print(f"{temp_c:.1f}°C  equivale a  {temp_f:.1f}°F")

    #Mensaje final
    print("\n" + "=" * 45)
    print("Gracias por usar el programa!")
    print(f"Desarrollado para {nombre_usuario} - {edad} años")
    print("=" * 45)


if __name__ == "__main__":
    main()