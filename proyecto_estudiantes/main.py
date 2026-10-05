from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import ClienteController, EstudianteController


class MenuClientes:
    """VISTA: muestra, pide y presenta. No decide reglas del negocio."""

    # ATRIBUTOS DE CLASE: lo que una subclase puede cambiar sin tocar la lógica
    TITULO = "SISTEMA DE GESTIÓN DE CLIENTES"
    ENTIDAD = "cliente"
    ENTIDADES = "clientes"
    TEXTO_BUSQUEDA = "Nombre, email, teléfono o ciudad"
    ANCHO = 85

    def __init__(self, controlador=ClienteController):
        # ATRIBUTOS DE INSTANCIA: estado de ESTE menú
        self.__controlador = controlador
        self.__activo = True
        # DICCIONARIO tecla -> (texto, método). Reemplaza al if/elif largo.
        self.__opciones = {
            "1": (f"Crear {self.ENTIDAD}", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "7": ("Estadísticas", self.estadisticas),
            "0": ("Salir", self.salir),
        }

    # ===== PROPIEDAD y MÉTODO para que las SUBCLASES (menús hijos) se apoyen en el padre =====
    @property
    def controlador(self):
        # Solo lectura: las subclases no pueden acceder a __controlador (el nombre se
        # transforma en _MenuClientes__controlador), así que se lo ofrecemos por aquí.
        return self.__controlador

    def agregar_opcion(self, tecla, texto, metodo):
        """Agrega una opción al menú dejando 'Salir' siempre al final."""
        salir = self.__opciones.pop("0")
        self.__opciones[tecla] = (texto, metodo)
        self.__opciones["0"] = salir

    # ===== ESTÁTICOS: utilidades de pantalla, no dependen del menú =====
    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        """Devuelve un entero o None si el usuario escribió cualquier otra cosa."""
        try:
            return int(input(etiqueta))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ===== MÉTODOS DE INSTANCIA =====
    def mostrar_tabla(self, clientes):
        print(f"{'ID':<5}{'NOMBRE':<25}{'EMAIL':<28}{'CIUDAD':<15}{'TELÉFONO':<12}")
        print("-" * self.ANCHO)
        for cliente in clientes:
            print(f"{cliente.id:<5}{cliente.nombre_completo:<25}"
                f"{cliente.email:<28}{cliente.ciudad:<15}{cliente.telefono:<12}")
        print("-" * self.ANCHO)
        imprimir_info(f"Total: {len(clientes)} {self.ENTIDAD}(s)")

    def mostrar_detalle(self, cliente):
        """Cómo se ve UN registro completo. Los menús hijos lo sobreescriben."""
        for clave, valor in cliente.a_diccionario().items():
            print(f"  {clave.capitalize():<12}: {valor}")
        imprimir_info(f"Dominio del email: {cliente.dominio_email}")

    def crear(self):
        imprimir_titulo(f"CREAR NUEVO {self.ENTIDAD.upper()}")
        # Recorro la TUPLA de campos del Modelo: si el Modelo cambia, el formulario también
        datos = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            datos[campo] = input(f"{campo.capitalize()}: ")
        exito, mensaje = self.__controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def listar(self):
        imprimir_titulo(f"LISTA DE {self.ENTIDADES.upper()}")
        registros = self.__controlador.listar()
        if not registros:
            imprimir_info(f"Todavía no hay {self.ENTIDADES}. Use la opción 1 para crear el primero.")
        else:
            self.mostrar_tabla(registros)
        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self.ENTIDAD.upper()}")
        termino = input(f"{self.TEXTO_BUSQUEDA}: ")
        encontrados = self.__controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Ningún {self.ENTIDAD} coincide con '{termino}'.")
        else:
            self.mostrar_tabla(encontrados)
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"VER {self.ENTIDAD.upper()} POR ID")
        id_registro = self.pedir_entero(f"Id del {self.ENTIDAD}: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()
        objeto = self.__controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un {self.ENTIDAD} con id {id_registro}")
        else:
            self.mostrar_detalle(objeto)
        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self.ENTIDAD.upper()}")
        id_registro = self.pedir_entero(f"Id del {self.ENTIDAD}: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()
        objeto = self.__controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un {self.ENTIDAD} con id {id_registro}")
            return self.pausa()
        imprimir_info(f"Editando a {objeto.nombre_completo}")
        print("Deje en blanco el campo que no quiera cambiar.\n")
        cambios = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            actual = getattr(objeto, campo)          # lee la PROPIEDAD
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo:
                cambios[campo] = nuevo
        self.mostrar_resultado(*self.__controlador.actualizar(id_registro, cambios))
        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self.ENTIDAD.upper()}")
        id_registro = self.pedir_entero(f"Id del {self.ENTIDAD}: ")
        if id_registro is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()
        objeto = self.__controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error(f"No existe un {self.ENTIDAD} con id {id_registro}")
            return self.pausa()
        imprimir_info(f"Se eliminará: {objeto}")
        if confirmar("¿Confirma la eliminación?"):
            self.mostrar_resultado(*self.__controlador.eliminar(id_registro))
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def estadisticas(self):
        imprimir_titulo("ESTADÍSTICAS")
        datos = self.__controlador.estadisticas()
        print(f"  Clientes registrados : {datos['total']}")
        print(f"  Ciudades distintas   : {len(datos['ciudades'])} -> {', '.join(datos['ciudades'])}")
        print(f"  Dominios de email    : {', '.join(datos['dominios'])}")
        print(f"  Sin teléfono         : {len(datos['sin_telefono'])}")
        self.pausa()

    def salir(self):
        self.__activo = False          # cambia el estado del objeto
        imprimir_info("¡Hasta luego! 👋")

    def mostrar_menu(self):
        imprimir_titulo(self.TITULO)
        for tecla, (texto, _metodo) in self.__opciones.items():
            print(f"  {tecla}. {texto}")
        print()

    def ejecutar(self):
        """El bucle principal: vive mientras __activo sea True."""
        while self.__activo:
            self.mostrar_menu()
            tecla = input("Seleccione una opción: ").strip()
            if tecla not in self.__opciones:
                imprimir_error("Opción no válida")
                self.pausa()
                continue
            _texto, metodo = self.__opciones[tecla]
            metodo()          # el diccionario guarda el método: aquí se ejecuta


class MenuEstudiantes(MenuClientes):
    """VISTA de estudiantes. HEREDA el menú completo y solo cambia lo que es distinto."""

    # Cambiamos los atributos de clase: el padre los usa en todos sus textos
    TITULO = "SISTEMA DE GESTIÓN DE ESTUDIANTES"
    ENTIDAD = "estudiante"
    ENTIDADES = "estudiantes"
    TEXTO_BUSQUEDA = "Nombre, apellido, email o carnet"
    ANCHO = 90

    def __init__(self, controlador=EstudianteController):
        super().__init__(controlador)          # el padre arma las opciones 1-7 y 0
        # Y aquí se agregan las opciones nuevas
        self.agregar_opcion("8", "Agregar nota", self.agregar_nota)
        self.agregar_opcion("9", "Ver promedio", self.ver_promedio)
        self.agregar_opcion("10", "Materias en común", self.materias_en_comun)

    # ===== ESTÁTICO: convertir lo que escribió el usuario es trabajo de la Vista =====
    @staticmethod
    def pedir_numero(etiqueta):
        """Devuelve un número (int o float) o None si no se pudo convertir."""
        try:
            valor = float(input(etiqueta).strip().replace(",", "."))
        except ValueError:
            return None
        return int(valor) if valor.is_integer() else valor

    # ===== SOBREESCRITURA: mismo nombre que el padre, otro comportamiento (polimorfismo) =====
    def mostrar_tabla(self, estudiantes):
        print(f"{'ID':<5}{'NOMBRE':<25}{'CARNET':<14}{'EMAIL':<28}{'PROM.':<8}{'ESTADO':<10}")
        print("-" * self.ANCHO)
        for estudiante in estudiantes:
            print(f"{estudiante.id:<5}{estudiante.nombre_completo:<25}"
                f"{estudiante.carnet:<14}{estudiante.email:<28}"
                f"{estudiante.promedio:<8}{estudiante.estado:<10}")
        print("-" * self.ANCHO)
        imprimir_info(f"Total: {len(estudiantes)} {self.ENTIDAD}(s)")

    def mostrar_detalle(self, estudiante):
        datos = estudiante.a_diccionario()
        for clave in ("id", "nombre", "apellido", "email", "carnet"):
            print(f"  {clave.capitalize():<12}: {datos[clave]}")
        materias = ", ".join(sorted(estudiante.materias)) or "(ninguna)"
        print(f"  {'Materias':<12}: {materias}")
        imprimir_info(f"Promedio: {estudiante.promedio} - {estudiante.estado}")

    def estadisticas(self):
        imprimir_titulo("ESTADÍSTICAS")
        datos = self.controlador.estadisticas()
        print(f"  Estudiantes registrados : {datos['total']}")
        print(f"  Aprobados               : {datos['aprobados']}")
        print(f"  Reprobados              : {datos['reprobados']}")
        print(f"  Materias ofertadas      : {len(datos['materias'])} -> {', '.join(datos['materias'])}")
        self.pausa()

    # ===== OPCIONES NUEVAS =====
    def agregar_nota(self):
        imprimir_titulo("AGREGAR NOTA")
        id_estudiante = self.pedir_entero("Id del estudiante: ")
        if id_estudiante is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()
        materia = input("Materia: ")
        nota = self.pedir_numero("Nota (0 a 20): ")
        if nota is None:
            imprimir_error("La nota debe ser un número")
            return self.pausa()
        self.mostrar_resultado(*self.controlador.agregar_nota(id_estudiante, materia, nota))
        self.pausa()

    def ver_promedio(self):
        imprimir_titulo("PROMEDIO DE UN ESTUDIANTE")
        id_estudiante = self.pedir_entero("Id del estudiante: ")
        if id_estudiante is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()
        estudiante = self.controlador.obtener(id_estudiante)
        if estudiante is None:
            imprimir_error(f"No existe un estudiante con id {id_estudiante}")
            return self.pausa()
        print(f"  Estudiante: {estudiante.nombre_completo} ({estudiante.carnet})\n")
        if not estudiante.materias:
            imprimir_info("Todavía no tiene materias ni notas.")
        for materia in sorted(estudiante.materias):
            print(f"  {materia:<20}: {estudiante.notas_de(materia)}")
        print()
        print(f"  Promedio general: {estudiante.promedio}")
        self.mostrar_resultado(estudiante.estado == "Aprobado", f"Estado: {estudiante.estado}")
        self.pausa()

    def materias_en_comun(self):
        imprimir_titulo("MATERIAS EN COMÚN")
        id_a = self.pedir_entero("Id del primer estudiante: ")
        id_b = self.pedir_entero("Id del segundo estudiante: ")
        if id_a is None or id_b is None:
            imprimir_error("Los ids deben ser números enteros")
            return self.pausa()
        exito, resultado = self.controlador.materias_en_comun(id_a, id_b)
        if not exito:
            imprimir_error(resultado)          # aquí 'resultado' es el mensaje de error
        elif not resultado:
            imprimir_info("No tienen materias en común.")
        else:
            imprimir_exito(f"Materias en común ({len(resultado)}):")
            for materia in sorted(resultado):
                print(f"  - {materia}")
        self.pausa()


if __name__ == "__main__":
    try:
        MenuEstudiantes().ejecutar()      # se crea el objeto y se lo pone a correr
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")