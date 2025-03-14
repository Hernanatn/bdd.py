from typing import Protocol, runtime_checkable, Self, TypeAlias, Optional, Any, AnyStr, Unpack,Union,Dict,List, get_origin
from decimal import Decimal
from datetime import datetime,date,time,timedelta,timezone
from re import Match

from chastack_bdd.tipos.enum_sql import *
from solteron import Solteron
### BDD
Resultado : TypeAlias = dict[str,Any]

class TipoCondicion:
    IGUAL = '='
    DIFERENTE = '!='
    MAYOR = '>'
    MENOR = '<'
    MAYOR_O_IGUAL = '>='
    MENOR_O_IGUAL = '<='
    NO_ES = 'IS NOT'

class TipoUnion:
    INNER = 'INNER'
    LEFT  = 'LEFT'
    RIGHT = 'RIGHT'
    FULL  = 'FULL'