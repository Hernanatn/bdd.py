# Referencia técnica detallada de chastack_bdd

Este documento detalla la interfaz pública y privada de las principales clases de chastack_bdd. Se listan las firmas, tipos y una breve descripción técnica de cada método o atributo relevante.

---

## Interfaz pública

### Registro

> [!TIP]    
> Todos los métodos constructores de clases con `metaclass=Tabla` aceptan el parámetro especial `debug: bool = False`.

#### Métodos de instancia
- `guardar() -> int`: Guarda el registro en la base de datos (crea o actualiza).
- `añadirRelacion(registro: Registro, tabla: str) -> None`: Agrega una relación muchos a muchos.
- `obtenerMuchos(tabla: str) -> dict[int, Registro]`: Devuelve registros relacionados.
- `borrarRelacion(registro: Registro, tabla: str) -> None`: Elimina una relación muchos a muchos.
- `__str__() -> str`: Representación tabular del registro.
- `__iter__() -> Iterator[tuple[str, Any]]`: Itera sobre (columna, valor) de los campos públicos.

#### Métodos de clase
- `devolverRegistros(bdd: ProtocoloBaseDeDatos, *, cantidad: int = 1000, indice: int = 0, orden: Optional[dict[str, TipoOrden]] = None, filtrosJoin: Optional[dict[str, str]] = None, **condiciones) -> tuple[Registro]`: Consulta registros.
- `atributos() -> list[str]`: Lista de atributos públicos.
- `inicializar(bdd: ProtocoloBaseDeDatos) -> None`: Fuerza la inicialización de la clase.

#### Métodos especiales
- `__init__(bdd: ProtocoloBaseDeDatos, valores: dict, *, debug: bool = False)`
- `__init__(bdd: ProtocoloBaseDeDatos, id: int, *, debug: bool = False)`

---

### Tabla y TablaIntermedia (metaclases)
- Uso indirecto: permiten la inicialización "vaga" y la sincronización automática de atributos.
- No exponen métodos públicos directos para el usuario final.

---

### `Usuario`

> [!TIP]    
> Todos los métodos constructores de clases con `metaclass=Tabla` aceptan el parámetro especial `debug: bool = False`.

#### Constructor
- `__init__(bdd, correo: str, contrasena: str, nombre_usuario: str = None, *, debug=False)`

#### Métodos de clase
- `registrar(bdd, correo: str, contrasena: str, nombre_usuario: str = None, **otros_campos) -> Usuario`: Registra un usuario.
- `ingresar(bdd, nombre_usuario: str, contrasena: str) -> Usuario`: Autentica por usuario/correo y contraseña.
- `ingresar(bdd, id_sesion: str) -> Usuario`: Autentica por id de sesión.

#### Métodos de instancia
- `cerrarSesion() -> None`: Cierra la sesión del usuario.
- `cambiarContraseña(contrasena_nueva: str) -> Self`: Cambia la contraseña.

#### Utilidades estáticas
- `encriptarContraseña(contrasena: str, sal: bytes = None) -> tuple[bytes, bytes]`



