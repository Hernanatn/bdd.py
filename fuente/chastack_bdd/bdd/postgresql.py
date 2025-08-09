
from chastack_bdd.tipos import *
from chastack_bdd.errores import *
from chastack_bdd.utiles import *
import chastack_bdd.bdd as chbdd
import psycopg
from psycopg.rows import dict_row


class ConfigPostgreSQL(metaclass=Solteron):
    __slots__ = (
        "__HOST",
        "__USUARIO",
        "__CONTRASENA",
        "__NOMBRE_BDD",
        "__PUERTO"
    )

    def __init__(self, host, usuario, contrasena, bdd, puerto=5432):
        self.__HOST = host
        self.__USUARIO = usuario
        self.__CONTRASENA = contrasena
        self.__NOMBRE_BDD = bdd
        self.__PUERTO = puerto

    @property
    def PARAMETROS_CONEXION(self) -> dict:
        return {
            "host": self.__HOST,
            "user": self.__USUARIO,
            "password": self.__CONTRASENA,
            "dbname": self.__NOMBRE_BDD,
            "port": self.__PUERTO,
            "row_factory": dict_row
        }


class BaseDeDatos_PostgreSQL:
    __slots__ = (
        "__config",
        "__conexion",
        "__cursor",
        "__consulta"
    )

    def __init__(self, configuracion: ConfigPostgreSQL = None) -> None:
        self.__conexion = None
        self.__cursor = None
        self.configurar(configuracion)
        self.__consulta = chbdd.Consulta()

    def configurar(self, configuracion: ConfigPostgreSQL = None) -> None:
        if configuracion:
            self.__config = configuracion
            return self

    def conectar(self) -> Self:
        if self.__conexion:
            return self
        self.__conexion = psycopg.connect(**self.__config.PARAMETROS_CONEXION)
        self.__cursor = self.__conexion.cursor()
        return self

    def desconectar(self) -> None:
        if self.__cursor:
            self.__cursor.close()
        if self.__conexion:
            self.__conexion.close()
        self.__cursor = None
        self.__conexion = None

    def reconectar(self) -> Self:
        self.desconectar()
        self.conectar()
        return self

    # Métodos del protocolo
    def DESCRIBE(self: Self, tabla: str) -> Self:
        self.__consulta = chbdd.Consulta(f"""
        SELECT
            a.attname AS "Field",
            CASE
                WHEN t.typcategory = 'E' THEN
                    'enum(' || (
                        SELECT string_agg(e.enumlabel, ',' ORDER BY e.enumsortorder)
                        FROM pg_enum e
                        WHERE e.enumtypid = t.oid
                    ) || ')'
                ELSE
                    format_type(a.atttypid, a.atttypmod)
            END AS "Type",
            CASE WHEN i.indisprimary THEN 'PRI' ELSE '' END AS "Key",
            pg_get_expr(ad.adbin, ad.adrelid) AS "Default",
            CASE WHEN a.attnotnull THEN 'NO' ELSE 'YES' END AS "Null",
            CASE
                WHEN t.typname IN ('int2', 'int4', 'int8')
                    AND pg_get_expr(ad.adbin, ad.adrelid) LIKE 'nextval%' THEN 'auto_increment'
                ELSE ''
            END AS "Extra"
        FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        JOIN pg_type t ON a.atttypid = t.oid
        LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
        LEFT JOIN pg_index i ON c.oid = i.indrelid AND a.attnum = ANY(i.indkey) AND i.indisprimary
        WHERE c.relname = '{tabla.lower()}'
        AND a.attnum > 0
        AND NOT a.attisdropped
        ORDER BY a.attnum;
        """)
        return self


    def SELECT(self, tabla: str, columnas: list[str], columnasSecundarias: Optional[dict[str, list[str]]] = {}) -> Self:
        self.__consulta.SELECT(tabla, columnas, columnasSecundarias)
        return self

    def DELETE(self, tabla: str) -> Self:
        self.__consulta.DELETE(tabla)
        return self

    def INSERT(self, tabla: str, **asignaciones: Unpack[dict[str, Any]]) -> Self:
        self.__consulta.RETURNING_ID()
        self.__consulta.INSERT(tabla, **asignaciones)
        return self

    def UPDATE(self, tabla: str, **asignaciones: Unpack[dict[str, Any]]) -> Self:
        self.__consulta.RETURNING_ID()
        self.__consulta.UPDATE(tabla, **asignaciones)
        return self

    def WHERE(self, tipoCondicion: TipoCondicion = TipoCondicion.IGUAL, **columnaValor: Unpack[dict[str, Any]]) -> Self:
        self.__consulta.WHERE(tipoCondicion, **columnaValor)
        return self

    def ORDER_BY(self, orden: [dict[str, TipoOrden]]):
        self.__consulta.ORDER_BY(orden)
        return self

    def JOIN(self, tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion: TipoUnion = TipoUnion.INNER) -> Self:
        self.__consulta.JOIN(tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion)
        return self

    def LIMIT(self, desplazamiento: int, limite: int) -> Self:
        # PostgreSQL usa LIMIT ... OFFSET ...
        if limite is not None:
            self.__consulta._Consulta__limite = f'LIMIT {limite} OFFSET {desplazamiento}\n'
        return self

    @sobrecargar
    def ejecutar(self, consulta: Union[chbdd.Consulta, str]) -> Optional[list[Resultado]]:
        if isinstance(consulta, chbdd.Consulta):
            consulta.RETURNING_ID()
            consulta = str(consulta)
        try:
            self.__cursor.execute(consulta)
            self.__conexion.commit()
        except Exception as e:
            self.reconectar()
            self.__cursor.execute(consulta)
            self.__conexion.commit()
        return self

    @sobrecargar
    def ejecutar(self) -> Optional[list[Resultado]]:
        print(f"[DEBUG]:\n\t{str(self.__consulta)}")
        try:
            self.__cursor.execute(str(self.__consulta))
            self.__conexion.commit()
        except Exception as e:
            self.reconectar()
            self.__cursor.execute(str(self.__consulta))
            self.__conexion.commit()
        self.__consulta.reiniciar()
        return self

    def devolverIdUltimaInsercion(self: Self) -> Optional[int]:
        try:
            return self.__cursor.fetchone()[0]
        except:
            return None

    def devolverResultados(self, cantidad: Optional[int] = None) -> Optional[list[dict]]:
        resultados = self.__cursor.fetchall()
        if not resultados:
            return None
        elif cantidad is None:
            return resultados
        elif cantidad == 0:
            return []
        elif cantidad > 0:
            return resultados[0:cantidad]
        else:
            raise IndexError("Cantidad negativa no válida.")

    def devolverUnResultado(self) -> Optional[dict]:
        return self.__cursor.fetchone()

    def estaConectado(self):
        return self.__conexion and not self.__conexion.closed

    def __enter__(self) -> 'BaseDeDatos_PostgreSQL':
        if self.__conexion is None:
            return self.conectar()
        return self

    def __exit__(self, exc_type, excl_val, exc_tb) -> None:
        self.desconectar()
