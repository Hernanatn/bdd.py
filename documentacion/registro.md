# Gestión de modelos: clases `Registro` y `Tabla`

La librería `chastack_bdd` permite definir modelos que reflejan tablas SQL de manera automática y segura, utilizando la metaclase `Tabla` y la clase base `Registro`.

> [!TIP]
> Todas las clases creadas con `metaclass=Tabla` aceptan el parámetro especial `debug`, que permite obtener información de diagnóstico sobre la inicialización, instanciación y otros eventos internos, facilitando el manejo de errores y la depuración.

**Importante:** Para utilizar esta funcionalidad, se debe crear una clase que herede de `Registro` (directa o indirectamente) y utilice `metaclass=Tabla`, por ejemplo:

```python
from chastack_bdd import Tabla, Registro

class Cliente(metaclass=Tabla):
    pass
```

Esta clase resultante (`Cliente` en el ejemplo) será la que se use para instanciar, consultar y manipular registros, siempre que la tabla SQL correspondiente cumpla con la estructura mínima requerida.

---

## Requisitos de la tabla

La tabla debe tener, como mínimo, los siguientes campos (ver equivalencias en [tipos SQL ↔ Python](./tipos_sql_python.md)):

- `id` (INT, PRIMARY KEY, AUTO_INCREMENT): Identificador único del registro.
- `fecha_carga` (DATETIME o TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Fecha y hora de creación del registro.
- `fecha_modificacion` (DATETIME o TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP): Fecha y hora de la última modificación.

Ver detalles y convenciones adicionales en [Requisitos de las tablas SQL](./requisitos_tablas.md).

---

## Métodos principales

### Constructor y registro

- `__init__(bdd, valores: dict, *, debug=False)`
  - Inicializa un registro a partir de un diccionario de valores.
- `__init__(bdd, id: int, *, debug=False)`
  - Inicializa un registro a partir de su id (sobrecarga).
- `guardar()`
  - Guarda el registro en la base de datos (crea o actualiza).

### Consultas y utilidades

- `devolverRegistros(bdd, *, cantidad=1000, indice=0, orden=None, filtrosJoin=None, **condiciones)`
  - Devuelve registros de la tabla según los filtros y orden indicados.
- `atributos()`
  - Devuelve la lista de atributos públicos de la clase.
- `inicializar(bdd)`
  - Fuerza la inicialización de la clase con la estructura de la tabla.
- `__str__()`
  - Devuelve una representación tabular del registro.
- `__iter__()`
  - Permite iterar sobre los campos del registro como pares `(columna, valor)`.

### Relaciones (opcional)

- `añadirRelacion(registro, tabla)`
  - Agrega una relación muchos a muchos con otro registro.
- `obtenerMuchos(tabla)`
  - Devuelve un diccionario con los registros relacionados de la tabla especificada.
- `borrarRelacion(registro, tabla)`
  - Elimina una relación muchos a muchos.

---

## Ejemplo de uso

```python
from chastack_bdd import Tabla, Registro, ConfigMySQL, BaseDeDatos_MySQL

class Cliente(metaclass=Tabla):
    pass

config = ConfigMySQL(
    host="localhost",
    usuario="root",
    contrasena="tu_contraseña",
    bdd="nombre_de_tu_base"
)
bdd = BaseDeDatos_MySQL(config)

# Crear un nuevo cliente
a = Cliente(bdd, {"nombre": "Ana", "email": "ana@ejemplo.com"})
a.guardar()

# Consultar un cliente existente por id
cliente = Cliente(bdd, id=1, debug=True)
print("Nombre:", cliente.nombre)
print("Email:", cliente.email)
print("Fecha de carga:", cliente.fecha_carga)

# Iterar sobre todos los campos del registro
for columna, valor in cliente:
    print(f"{columna}: {valor}")
```

---

## Notas

- Los atributos de la clase se sincronizan automáticamente con los campos de la tabla SQL.
- Los campos no modificables (`id`, `fecha_carga`, `fecha_modificacion`) están protegidos contra escritura directa.
- El parámetro `debug` es útil para depuración y diagnóstico durante el desarrollo.

---

## Personalización

Las clases basadas en `Registro` pueden ser extendidas para agregar métodos o lógica adicional, siempre que se respeten los campos mínimos requeridos para la integración con chastack_bdd. 