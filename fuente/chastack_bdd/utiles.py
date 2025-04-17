from json import dumps,loads
from chastack_bdd.tipos import *
from solteron import Solteron
from sobrecargar import sobrecargar
from secrets import token_urlsafe
from re import findall,match
def formatearValorParaSQL(valor: Any, html : bool = False) -> str:
    """
    Formatea un valor de Python a una representación adecuada para SQL.
    """
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, (list, tuple)):
        return f"'[{','.join(f"\"{str(v)}\"" for v in valor)}]'"
    if isinstance(valor, Decimal):
        return str(valor.to_eng_string())
    if isinstance(valor, (date, datetime, time)):
        return f"'{valor.isoformat()}'"
    if isinstance(valor, dict):
        return f"'{dumps(valor)}'"
    if isinstance(valor, bytes):
        return f"X'{valor.hex()}'"
    if isinstance(valor, Enum):
        return str(valor.value) if isinstance(valor.value, int) else f"'{valor.name}'"
    if isinstance(valor, str):
        return f"'{valor.replace("'", "''")}'"
        
    return f"'{str(valor).replace("'", "''")}'"

def atributoPublico(nombre_atributo: str) -> str:
    return nombre_atributo.replace('__','',1)

def atributoPrivado(obj: Any, nombre_atributo: str) -> str:
    return f"_{obj.__class__.__name__}__{atributoPublico(nombre_atributo)}"

def tieneAtributoPrivado(obj: Any, nombre_atributo: str) -> bool:
    return hasattr(obj,atributoPrivado(obj,nombre_atributo))

def devolverAtributoPrivado(obj: Any, nombre_atributo: str, por_defecto = None) -> Any:
    return getattr(obj,atributoPrivado(obj,nombre_atributo), por_defecto)

def asignarAtributoPrivado(obj: Any, nombre_atributo: str, valor) -> None:
    setattr(obj,atributoPrivado(obj,nombre_atributo), valor)

def devolverAtributo(obj: Any, nombre_atributo: str, por_defecto = None) -> Any:
    return getattr(obj,atributoPrivado(obj,nombre_atributo) if '__' in nombre_atributo else nombre_atributo, por_defecto)