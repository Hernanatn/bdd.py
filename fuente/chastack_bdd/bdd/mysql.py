from chastack_bdd.tipos import *
from chastack_bdd.errores import *
from chastack_bdd.utiles import *
import chastack_bdd.bdd as chbdd
from mysql.connector import connect


class ConfigMySQL(metaclass=Solteron):

    __slots__ = (
        '__HOST',  
        '__USUARIO',  
        '__CONTRASENA',  
        '__NOMBRE_BDD'
    )

    def __init__(self, host, usuario, contrasena, bdd):
        self.__HOST = host
        self.__USUARIO = usuario
        self.__CONTRASENA = contrasena
        self.__NOMBRE_BDD = bdd
    @property
    def PARAMETROS_CONEXION(self) -> dict: 
        return \
        {
            "host" : self.__HOST,
            "user" : self.__USUARIO,
            "password" : self.__CONTRASENA,
            "database" : self.__NOMBRE_BDD,
            "use_pure" : False
        }

    @property
    def OPCION_CURSOR(self) -> dict:
        return \
        {
           "dictionary" : True,
           "named_tuple" : False,   
        }

class BaseDeDatos_MySQL():
    _slots__ = \
    (
        "__config",
        "__conexion",
        "__cursor",
        "__consulta"
    )
    def __init__(self, configuracion : ConfigMySQL = None) -> None:
        self.__conexion = None
        self.__cursor = None
        self.configurar(configuracion)
        self.__consulta = chbdd.Consulta()
    
    def configurar(self, configuracion : ConfigMySQL = None) -> None:
        if configuracion:
            self.__config = configuracion
            return self
        # Agregar comportamiento usando las variables de ambiente

    def conectar(self) -> Self:
        if self.__conexion: return self
        self.__conexion = connect(**self.__config.PARAMETROS_CONEXION)
        self.__cursor = self.__conexion.cursor(buffered=True, **self.__config.OPCION_CURSOR)
        return self

    def desconectar(self) -> None:
        if self.__cursor: self.__cursor.close()
        if self.__conexion: self.__conexion.close()
        self.__cursor = None
        self.__conexion = None
    
    def reconectar(self) -> Self:
        self.desconectar()
        self.conectar()
        return self
    
    def DESCRIBE(self: Self, tabla :str) -> Self:
        self.__consulta.DESCRIBE(tabla)
        return self 
    def SELECT(self, tabla : str, columnas : list[str], columnasSecundarias: Optional[dict[str, list[str]] ] = {}) -> Self:
        self.__consulta.SELECT(tabla, columnas, columnasSecundarias)
        return self
    def DELETE(self, tabla : str) -> Self: 
        self.__consulta.DELETE(tabla)
        return self
    def INSERT(self, tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self: 
        self.__consulta.INSERT(tabla, **asignaciones)
        return self
    def UPDATE(self, tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self: 
        self.__consulta.UPDATE( tabla, **asignaciones)
        return self
    def WHERE(self, tipoCondicion : TipoCondicion = TipoCondicion.IGUAL , **columnaValor : Unpack[dict[str, Any]]) -> Self: 
        self.__consulta.WHERE(tipoCondicion, **columnaValor)
        return self
    def ORDER_BY(self, orden : [dict[str, TipoOrden]]):
        self.__consulta.ORDER_BY(orden)
        return self
    def JOIN(self,   tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion : TipoUnion = TipoUnion.INNER) -> Self: 
        self.__consulta.JOIN(tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion)
        return self
    def LIMIT(self, desplazamiento: int  , limite : int) -> Self: 
        self.__consulta.LIMIT(desplazamiento, limite)
        return self
   
    @sobrecargar
    def ejecutar(self, consulta : Union[chbdd.Consulta,str]) -> Optional[list[Resultado]] :
        if isinstance(consulta,chbdd.Consulta):
            consulta = str(consulta)
        try:
            self.__cursor.execute(consulta)
            self.__conexion.commit()
        except ErrorBDD as e:
            ###print(f"[ERROR] {e}")
            self.reconectar()
            self.__cursor.execute(consulta)
            self.__conexion.commit()
        except AttributeError as e:
            ###print(f"[ERROR] {e}")
            self = BaseDeDatos_MySQL()
            self.conectar()
            self.__cursor.execute(consulta)
            self.__conexion.commit()
        except Exception as f:
            raise type(f)(f"No se pudo completar la consulta.\n Es probable que la consulta incluya carácteres prohibidos. \n {consulta.encode('utf-8').decode('unicode_escape')}\n") from f
        return self

    @sobrecargar
    def ejecutar(self) -> Optional[list[Resultado]] :

        try:
            self.__cursor.execute(str(self.__consulta))
            self.__conexion.commit()
        except ErrorBDD as e:
            ###print(f"[ERROR] {e}")
            self.reconectar()
            self.__cursor.execute(str(self.__consulta))
            self.__conexion.commit()
        except AttributeError as e:
            ###print(f"[ERROR] {e}")
            self = BaseDeDatos_MySQL()
            self.conectar()
            self.__cursor.execute(str(self.__consulta))
            self.__conexion.commit()
        except Exception as f:
            raise type(f)(f"No se pudo completar la consulta.\n Es probable que la consulta incluya carácteres prohibidos. \n {str(self.__consulta).encode('utf-8').decode('unicode_escape')}\n") from f
        
        self.__consulta.reiniciar()
        return self
   
    def devolverIdUltimaInsercion(self : Self) -> Optional[int]:
        return self.__cursor.lastrowid
        
    def devolverResultados(self, cantidad : Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        resultados = self.__cursor.fetchall()
        
        if not resultados: return None
        elif cantidad is None: return resultados
        elif cantidad == 0: return []
        elif cantidad > 0: return resultados[0:cantidad-1]
        else: raise IndexError("Se solicitó una cantidad negativa de resultados, lo cual es un sinsentido.")
    def devolverUnResultado(self) -> Optional[Dict[str, Any]]:
        """
        Devuelve el primer resultado de la última consulta.
        """
        return self.__cursor.fetchone()
        
    # Estados
    def estaConectado (self):
            return self.__conexion.is_connected() if self.__conexion else False



  # with BaseDeDatos() as bdd
    def __enter__(self) -> 'BaseDeDatos_MySQL':
        if self.__conexion is None:
            return self.conectar()
        # ###print(f"[DEBUG] Entrando {self.__cursor=}{self.__conexion=}{self.__pool=}")
        return self

    def __exit__(self, exc_type,excl_val,exc_tb) -> None:
        # ###print(f"[DEBUG] Saliendo {self.__cursor=}{self.__conexion=}{self.__pool=}")
        self.desconectar()
