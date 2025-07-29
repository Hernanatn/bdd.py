# Protocolo de base de datos y personalización

chastack_bdd define un protocolo de base de datos (`ProtocoloBaseDeDatos`) que abstrae las operaciones fundamentales necesarias para interactuar con cualquier motor de base de datos relacional.

## Métodos requeridos por el protocolo

Se debe implementar una clase que provea los siguientes métodos:

- `DESCRIBE(tabla: str) -> Self`
- `SELECT(tabla: str, columnas: list[str], columnasSecundarias: Optional[dict[str, list[str]]] = {}) -> Self`
- `DELETE(tabla: str) -> Self`
- `INSERT(tabla: str, **asignaciones) -> Self`
- `UPDATE(tabla: str, **asignaciones) -> Self`
- `WHERE(tipoCondicion, **columnaValor) -> Self`
- `JOIN(tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion) -> Self`
- `ORDER_BY(orden) -> Self`
- `LIMIT(desplazamiento, limite) -> Self`
- `__enter__() -> Self`
- `__exit__(exc_type, excl_val, exc_tb) -> None`
- `ejecutar() -> Self`
- `devolverUnResultado() -> Resultado`
- `devolverResultados() -> tuple[Resultado]`
- `devolverIdUltimaInsercion() -> Optional[int]`

## Ejemplo de implementación propia

Se puede implementar una clase que cumpla con el protocolo para usar otro motor de base de datos (por ejemplo, PostgreSQL):

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from chastack_bdd import ProtocoloBaseDeDatos
from solteron import Solteron

class ConfigPostgreSQL(metaclass=Solteron):
    """
    Configuración para la conexión a PostgreSQL.
    """
    def __init__(self, host, usuario, contrasena, bdd, puerto=5432):
        self.host = host
        self.usuario = usuario
        self.contrasena = contrasena
        self.bdd = bdd
        self.puerto = puerto

    @property
    def PARAMETROS_CONEXION(self):
        return {
            "host": self.host,
            "user": self.usuario,
            "password": self.contrasena,
            "dbname": self.bdd,
            "port": self.puerto
        }

    @property
    def OPCION_CURSOR(self):
        return {
            "cursor_factory": RealDictCursor
        }

class BaseDeDatos_PostgreSQL():
    def __init__(self, config: ConfigPostgreSQL):
        self.config = config
        self.conexion = None
        self.cursor = None
        self._consulta = None  # En este ejemplo no utilizamos la clase `Consulta` en su lugar implementamos todo directo en baseDeDatos_Postgres

    def conectar(self):
        if self.conexion is None:
            self.conexion = psycopg2.connect(**self.config.PARAMETROS_CONEXION)
            self.cursor = self.conexion.cursor(**self.config.OPCION_CURSOR)
        return self

    def desconectar(self):
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        self.cursor = None
        self.conexion = None

    def __enter__(self):
        return self.conectar()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()

    def DESCRIBE(self, tabla):
        self._consulta = f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = '{tabla}';"
        return self

    def SELECT(self, tabla, columnas, columnasSecundarias={}):
        cols = ', '.join(columnas)
        self._consulta = f"SELECT {cols} FROM {tabla}"
        # No se implementa JOIN ni columnas secundarias en este ejemplo mínimo
        return self

    def DELETE(self, tabla):
        self._consulta = f"DELETE FROM {tabla}"
        return self

    def INSERT(self, tabla, **asignaciones):
        columnas = ', '.join(asignaciones.keys())
        valores = ', '.join(['%s'] * len(asignaciones))
        self._consulta = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores}) RETURNING id"
        self._valores = list(asignaciones.values())
        return self

    def UPDATE(self, tabla, **asignaciones):
        set_clause = ', '.join([f"{k} = %s" for k in asignaciones.keys()])
        self._consulta = f"UPDATE {tabla} SET {set_clause} WHERE id = %s"
        self._valores = list(asignaciones.values())
        # El id debe ser pasado aparte en la lógica de uso
        return self

    def WHERE(self, tipoCondicion=None, **columnaValor):
        if columnaValor:
            condiciones = ' AND '.join([f"{k} = %s" for k in columnaValor.keys()])
            if "WHERE" in self._consulta:
                self._consulta += f" AND {condiciones}"
            else:
                self._consulta += f" WHERE {condiciones}"
            if hasattr(self, '_valores'):
                self._valores += list(columnaValor.values())
            else:
                self._valores = list(columnaValor.values())
        return self

    def ORDER_BY(self, orden):
        if orden:
            orden_sql = ', '.join([f"{col} {dir}" for col, dir in orden.items()])
            self._consulta += f" ORDER BY {orden_sql}"
        return self

    def LIMIT(self, desplazamiento, limite):
        self._consulta += f" LIMIT {limite} OFFSET {desplazamiento}"
        return self

    def ejecutar(self):
        self.conectar()
        try:
            if hasattr(self, '_valores'):
                self.cursor.execute(self._consulta, self._valores)
            else:
                self.cursor.execute(self._consulta)
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise
        return self

    def devolverUnResultado(self):
        return self.cursor.fetchone()

    def devolverResultados(self):
        return self.cursor.fetchall()

    def devolverIdUltimaInsercion(self):
        # En PostgreSQL, se puede obtener el id con RETURNING en el INSERT
        if self.cursor.description and self.cursor.rowcount > 0:
            res = self.cursor.fetchone()
            if res and 'id' in res:
                return res['id']
        return None
```

Luego, se puede utilizar la nueva implementación al instanciar los modelos:

```python
config = ConfigPostgreSQL(
    host="localhost",
    usuario="usuario",
    contrasena="contraseña",
    bdd="nombre_de_la_bdd"
)
bdd = BaseDeDatos_PostgreSQL(config)
cliente = Cliente(bdd, id=1)
```

## Implementación incluida: MySQL

La librería incluye una implementación lista para usar con MySQL (`BaseDeDatos_MySQL`).

## Notas

- Se recomienda respetar la semántica de los métodos para garantizar compatibilidad.
- El protocolo permite desacoplar la lógica de los modelos del motor de base de datos subyacente. 
