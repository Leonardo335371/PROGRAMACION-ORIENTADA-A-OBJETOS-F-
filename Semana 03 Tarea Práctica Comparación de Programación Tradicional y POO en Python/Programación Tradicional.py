# Programación Tradicional: Cálculo del promedio semanal de temperaturas


def ingresar_temperaturas_dia(dia):
    """
    Función para ingresar las temperaturas de un día específico.
    - Recibe el nombre del día como parámetro.
    - Solicita 3 temperaturas (mañana, tarde, noche).
    - Valida que sean números válidos.
    - Calcula y retorna el promedio diario.
    - Incluye mensajes claros para el usuario.
    """
    print(f"Ingresando temperaturas para el {dia}:")
    temps = []
    for momento in ["mañana", "tarde", "noche"]:
        while True:
            try:
                temp = float(input(f"Temperatura de la {momento} (en °C): "))
                temps.append(temp)
                break
            except ValueError:
                print("Por favor, ingrese un valor numérico válido.")
    promedio_dia = sum(temps) / len(temps)
    print(f"Promedio del {dia}: {promedio_dia:.2f} °C\n")
    return promedio_dia


def calcular_promedio_semanal():
    """
    Función principal que organiza el flujo del programa.
    - Define la lista de días de la semana.
    - Llama a ingresar_temperaturas_dia() para cada día.
    - Almacena los promedios diarios.
    - Calcula el promedio semanal.
    - Muestra un resumen claro de todos los valores.
    Esta función actúa como el "orquestador" del proceso.
    """
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    promedios_diarios = []

    print("=== Cálculo del Promedio Semanal de Temperaturas ===\n")

    # Entrada de datos para cada día usando la función
    for dia in dias_semana:
        promedio_dia = ingresar_temperaturas_dia(dia)
        promedios_diarios.append(promedio_dia)

    # Cálculo del promedio semanal
    promedio_semanal = sum(promedios_diarios) / len(promedios_diarios)

    # Mostrar resultados
    print("=== Resumen Semanal ===")
    for i, dia in enumerate(dias_semana):
        print(f"{dia}: {promedios_diarios[i]:.2f} °C")
    print(f"\nPromedio semanal: {promedio_semanal:.2f} °C")

    return promedio_semanal


# Ejecución del programa
if __name__ == "__main__":
    calcular_promedio_semanal()