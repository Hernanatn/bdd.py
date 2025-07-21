# Gestión de usuarios: clase `Usuario`

La librería `chastack_bdd` incluye una clase base especial `Usuario` que extiende la funcionalidad de los modelos para cubrir los casos de gestión de usuarios, autenticación y manejo seguro de contraseñas y sesiones.

> **Nota:** Cualquier subclase de `Usuario` (y en general cualquier heredero de `Registro`) permite iterar sobre sus columnas y valores con `for columna, valor in instancia:`.

**Importante:** Para utilizar esta funcionalidad, se debe crear una subclase que herede de `Usuario` y utilice `metaclass=Tabla`, por ejemplo:

```python
from chastack_bdd import Tabla, Usuario

class MiUsuario(Usuario, metaclass=Tabla):
    pass
```

Esta clase resultante (`MiUsuario` en el ejemplo) será la que se use para instanciar, autenticar y gestionar usuarios, siempre que la tabla SQL correspondiente cumpla con la estructura mínima requerida.

---

## Requisitos de la tabla `Usuario`

La tabla debe tener, además de los campos mínimos de [Registro](./requisitos_tablas.md), los siguientes campos (ver equivalencias en [tipos SQL ↔ Python](./tipos_sql_python.md)):

- `nombre_usuario` (varchar, único)
- `correo` (varchar, único)
- `contrasena` (varbinary)
- `sal` (varbinary)
- `id_sesion` (varchar, único, puede ser NULL)
- `codigo_unico` (varchar, puede ser NULL)
- `fecha_ultimo_ingreso` (timestamp)

Ver definición en [`usuario.sql`](../fuente/chastack_bdd/usuario/usuario.sql).

---

## Métodos principales

### Constructor y registro

- `__init__(bdd, correo: str, contrasena: str, nombre_usuario: str = None, *, debug=False)`
  - Crea un nuevo usuario, encriptando la contraseña y generando los campos de sesión.
- `registrar(bdd, correo: str, contrasena: str, nombre_usuario: str = None, **otros_campos)`
  - Registra un usuario y permite agregar campos adicionales.

### Autenticación y sesión

- `ingresar(bdd, nombre_usuario: str, contrasena: str) -> Usuario`
  - Autentica un usuario por nombre o correo y contraseña.
- `ingresar(bdd, id_sesion: str) -> Usuario`
  - Recupera un usuario por su id de sesión.
- `cerrarSesion()`
  - Cierra la sesión del usuario.

### Contraseña y seguridad

- `cambiarContraseña(contrasena_nueva: str) -> Self`
  - Cambia la contraseña del usuario, encriptando la nueva.
- `encriptarContraseña(contrasena: str, sal: bytes = None) -> tuple[bytes, bytes]` (estático)
  - Encripta una contraseña usando SHA-256, sal y pimienta.
- `__verificarContraseña(contrasena_encriptada: bytes, contrasena: str, sal: bytes) -> bool` (estático)
  - Verifica si una contraseña coincide con su hash.

### Utilidades

- `__generarIdSesion() -> str` (estático)
  - Genera un identificador de sesión seguro.
- `_actualizarFechaIngreso(fecha_ultimo_ingreso: datetime = datetime.now())`
  - Actualiza la fecha del último ingreso.

---

## Ejemplo de uso

```python
from chastack_bdd import Tabla, Usuario

class MiUsuario(Usuario, metaclass=Tabla):
    pass

# Registro de un nuevo usuario
db = BaseDeDatos_MySQL(config)
usuario = MiUsuario(db, correo="ana@ejemplo.com", contrasena="secreta")
usuario.guardar()

# Autenticación
autenticado = MiUsuario.ingresar(db, nombre_usuario="ana@ejemplo.com", contrasena="secreta")
print(autenticado.id_sesion)

# Iterar sobre los campos del usuario autenticado
for columna, valor in autenticado:
    print(f"{columna}: {valor}")

# Cambio de contraseña
autenticado.cambiarContraseña("nueva_clave")

# Cierre de sesión
autenticado.cerrarSesion()
```

---

## Notas de seguridad

- Se utiliza encriptado SHA-256 con sal y "pimienta" (variable de entorno `PIMIENTA`).
- Las contraseñas nunca se almacenan en texto plano.
- Se recomienda definir correctamente los índices únicos y restricciones en la tabla SQL.

---

## Personalización

La clase `Usuario` puede ser extendida para agregar campos o métodos adicionales, siempre que se respeten los campos mínimos requeridos para la autenticación y gestión de sesiones. 