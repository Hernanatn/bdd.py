# Requisitos de las tablas SQL

Para que una tabla pueda ser utilizada con `chastack_bdd`, se deben cumplir los siguientes requisitos mínimos:

## Campos obligatorios

- `id` (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único del registro.
- `fecha_carga` (DATETIME o TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Fecha y hora de creación del registro.
- `fecha_modificacion` (DATETIME o TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP): Fecha y hora de la última modificación.

Ver [Equivalencia de tipos SQL ↔ Python](#equivalencia-de-tipos-sql--python) para el mapeo correcto de tipos.

## Convenciones adicionales

- El nombre de la tabla debe coincidir exactamente con el nombre de la clase (respetando mayúsculas/minúsculas).
- Los campos que sean claves foráneas o participen en relaciones deben estar correctamente definidos a nivel SQL.
- Los campos automáticos (`id`, `fecha_carga`, `fecha_modificacion`) serán protegidos contra escritura directa desde la instancia.

## Ejemplo de definición SQL

```sql
CREATE TABLE Cliente (
    id INT PRIMARY KEY AUTO_INCREMENT
    , fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP
    , fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    , nombre VARCHAR(100) NOT NULL
    , email VARCHAR(100) NOT NULL
);
```



## Equivalencia de tipos SQL ↔ Python

Esta tabla resume la correspondencia entre los tipos de datos SQL (MySQL) y los tipos de Python utilizados internamente por chastack_bdd, según la lógica de `Tabla.__resolverTipo`.

| Tipo MySQL           | Tipo Python      | Notas                       |
|--------------------|------------------|----------------------------------------|
| tinyint            | int              |                                        |
| smallint           | int              |                                        |
| mediumint          | int              |                                        |
| int                | int              |                                        |
| bigint             | int              |                                        |
| float              | float            |                                        |
| double             | float            |                                        |
| decimal            | Decimal          | externo: decimal.Decimal            |
| datetime           | datetime         | externo: datetime.datetime          |
| timestamp          | datetime         | externo: datetime.datetime          |
| date               | date             | externo: datetime.date              |
| time               | time             | externo: datetime.time              |
| char               | str              |                                        |
| varchar            | str              |                                        |
| text               | str              |                                        |
| mediumtext         | str              |                                        |
| longtext           | str              |                                        |
| tinytext           | str              |                                        |
| boolean            | bool             |                                        |
| bool               | bool             |                                        |
| tinyint(1)         | bool             |                                        |
| blob               | bytearray        |                                        |
| mediumblob         | bytearray        |                                        |
| longblob           | bytearray        |                                        |
| tinyblob           | bytearray        |                                        |
| binary             | bytes            |                                        |
| varbinary          | bytes            |                                        |
| json               | dict             |                                        |
| enum(...)          | Enum_SQL             | Se genera un Enum dinámico en Python externo: chastack_bdd.Enum_SQL  |

> [!TIP]  
> Los campos `enum` generan una subclase de Enum en tiempo de ejecución.  
> Si el tipo SQL no está en la lista, se mapea a `Any` (tipado dinámico).  

## Notas

- Se recomienda definir índices y restricciones adicionales según las necesidades del modelo de datos.
- Las tablas intermedias para relaciones muchos a muchos deben tener al menos los campos `id_tabla1`, `id_tabla2` y los campos de auditoría mencionados. 