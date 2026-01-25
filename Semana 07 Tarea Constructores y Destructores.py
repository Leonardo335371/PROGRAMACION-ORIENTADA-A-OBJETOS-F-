# Programa para demostrar el uso de constructores y destructores

import os  # Módulo para manejar operaciones del sistema operativo, como borrar archivos.


class ManejadorArchivo:
    """
    Clase que demuestra el uso de constructor y destructor para manejar un archivo temporal.
    - En el constructor: Crea y abre un archivo temporal, inicializa atributos.
    - En el destructor: Cierra el archivo y lo elimina para limpiar recursos.
    """

    def __init__(self, nombre_archivo='temp.txt', contenido_inicial='Hola, mundo!'):
        """
        Constructor: Se ejecuta al crear el objeto.
        - Inicializa los atributos: nombre del archivo y el manejador del archivo.
        - Abre el archivo en modo escritura y escribe el contenido inicial.
        """
        self.nombre_archivo = nombre_archivo
        self.archivo = open(self.nombre_archivo, 'w')  # Abre el archivo en modo escritura.
        self.archivo.write(contenido_inicial)  # Escribe el contenido inicial.
        self.archivo.flush()  # Asegura que los cambios se escriban en el disco.
        print(f"Constructor llamado: Archivo '{self.nombre_archivo}' creado y escrito con '{contenido_inicial}'.")

    def leer_contenido(self):
        """
        Método para leer el contenido del archivo (demostración de uso del objeto).
        """
        self.archivo.seek(0)  # Vuelve al inicio del archivo.
        contenido = self.archivo.read()
        print(f"Contenido leído: {contenido}")
        return contenido

    def __del__(self):
        """
        Destructor: Se ejecuta cuando el objeto se destruye.
        - Cierra el archivo si está abierto.
        - Elimina el archivo del sistema para limpiar recursos.
        """
        if hasattr(self, 'archivo') and not self.archivo.closed:
            self.archivo.close()  # Cierra el archivo.
        if os.path.exists(self.nombre_archivo):
            os.remove(self.nombre_archivo)  # Elimina el archivo.
        print(f"Destructor llamado: Archivo '{self.nombre_archivo}' cerrado y eliminado.")


# Demostración del programa
if __name__ == "__main__":
    print("Iniciando demostración...")

    # Crear una instancia: Llama al constructor.
    manejador = ManejadorArchivo('mi archivo.txt', 'Prueba.')

    # Usar el objeto: Leer el contenido.
    manejador.leer_contenido()

    # Eliminar la referencia explícitamente para forzar la llamada al destructor.
    del manejador

    print("Fin de la demostración.")