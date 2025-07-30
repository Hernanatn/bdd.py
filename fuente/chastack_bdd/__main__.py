


#  HACER: Generar las clases que heredan de Tabla (y TablaIntermedia)
#  HACER: como un módulo estático sin cosas en tiempo de ejecución


from chastack_bdd.tipos.enum_sql import EnumSql
import pathlib as pl
import typing as t
import inspect


class Modelo:
    __slots__ = (
        "tipo",
        "nombre",
        "nombre_modulo",
        "ruta_absoluta",
        "ruta_relativa",
        "es_intermedia"
    )

    tipo: type
    nombre: str
    nombre_modulo: str
    ruta_absoluta: pl.Path
    ruta_relativa: pl.Path
    es_intermedia: bool

    def __init__(
        self,
        tipo: type,
        nombre: str,
        nombre_modulo: str,
        ruta_absoluta: pl.Path,
        ruta_relativa: pl.Path,
        es_intermedia: bool
    ) -> None:
        self.tipo = tipo
        self.nombre = nombre
        self.nombre_modulo = nombre_modulo
        self.ruta_absoluta = ruta_absoluta
        self.ruta_relativa = ruta_relativa
        self.es_intermedia = es_intermedia


#* 1: Descubrir clases que usan metaclass=Tabla o TablaIntermedia

def descubrirClasesDesdePaquete(ruta_paquete: pl.Path) -> list[type]:
    """
    Busca recursivamente clases Python que usen metaclass=Tabla o TablaIntermedia.
    """
    clases: list[type] = []

    # pseudocódigo:
    # for archivo in ruta_paquete.rglob("*.py"):
    #     modulo = importarModuloDesdeArchivo(archivo)
    #     for atributo in dir(modulo):
    #         posible_clase = getattr(modulo, atributo)
    #         if isinstance(posible_clase, type) and tieneMetaclaseValida(posible_clase):
    #             clases.append(posible_clase)

    return clases


#* 2: Instanciar clase para inicializar dinámicamente

def poblarClaseDesdeInstancia(clase: type, base_datos: ProtocoloBaseDeDatos) -> None:
    """
    Fuerza la inicialización dinámica de la clase instanciándola una vez.
    """
    _ = clase(base_datos, debug=False)


#* 3: Extraer __slots__ y __annotations__

def extraerEstructuraClase(clase: type) -> tuple[list[str], dict[str, type]]:
    """
    Devuelve la estructura de la clase: slots y anotaciones tipadas.
    """
    slots: list[str] = list(getattr(clase, "__slots__", []))
    anotaciones: dict[str, type] = dict(getattr(clase, "__annotations__", {}))
    return slots, anotaciones


#* 4: Detectar enums dinámicos definidos en la clase

def extraerEnumSqlsDesdeClase(clase: type) -> dict[str, type[EnumSql]]:
    """
    Recupera los enums dinámicamente definidos mediante __resolverTipo.
    """
    enums: dict[str, type[EnumSql]] = {}

    for nombre, valor in clase.__dict__.items():
        if isinstance(valor, type) and issubclass(valor, EnumSqlSQL):
            enums[nombre] = valor

    return enums


#* 5: Detectar propiedades inyectadas (ej. id, tabla)

def extraerPropiedadesDesdeClase(clase: type) -> dict[str, property]:
    """
    Recupera todas las propiedades definidas o inyectadas en la clase.
    """
    props: dict[str, property] = {}

    for nombre, valor in clase.__dict__.items():
        if isinstance(valor, property):
            props[nombre] = valor

    return props


#* 6: Extraer el código fuente de métodos deseados

def extraerCodigoFuenteMetodos(clase: type, nombres_metodos: list[str]) -> dict[str, str]:
    """
    Devuelve el código fuente (como texto plano) de cada método listado.
    """
    codigo: dict[str, str] = {}

    for nombre in nombres_metodos:
        metodo = clase.__dict__.get(nombre)
        if metodo is not None:
            try:
                codigo[nombre] = inspect.getsource(metodo)
            except OSError:
                continue  # No se puede recuperar (ej: métodos internos o compilados)

    return codigo


#* 7: Generar la definición completa en Python como string

def generarCodigoClaseEstatico(
    nombre_clase: str,
    slots: list[str],
    anotaciones: dict[str, type],
    enums: dict[str, type[EnumSql]],
    propiedades: dict[str, property],
    metodos_fuente: dict[str, str],
    origen: pl.Path,
    fecha: str
) -> str:
    """
    Ensambla la definición completa de clase en Python, sin dependencia de metaclase.
    """
    codigo: list[str] = []

    # pseudocódigo:
    # 1. Añadir encabezado con comentarios de origen y fecha
    # 2. Añadir imports necesarios (datetime, EnumSqlSQL, Registro, etc.)
    # 3. Generar cada enum como: class Nombre(EnumSqlSQL, EnumSql): ...
    # 4. Definir class NombreClase(Registro):
    #    - __slots__ = (...)
    #    - atributos tipados
    #    - propiedades con @property
    #    - métodos extraídos (como __str__, __iter__, etc.)

    return "\n".join(codigo)


#* 8: Escribir el archivo resultante

def guardarCodigo(ruta_archivo: pl.Path, contenido: str) -> None:
    """
    Escribe el contenido generado en el archivo destino.
    """
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
    ruta_archivo.write_text(contenido, encoding="utf-8")


#* 9: Validar equivalencia estructural

def validarEquivalenciaBasica(clase_dinamica: type, clase_estatica: type, base_datos: ProtocoloBaseDeDatos) -> bool:
    """
    Compara slots y anotaciones de dos clases para verificar equivalencia estructural.
    """
    slots_dinamica, anot_dinamica = extraerEstructuraClase(clase_dinamica)
    slots_estatica, anot_estatica = extraerEstructuraClase(clase_estatica)
    return slots_dinamica == slots_estatica and anot_dinamica == anot_estatica



def main() -> None:
    return

if __name__ == "__main__":
    main()


