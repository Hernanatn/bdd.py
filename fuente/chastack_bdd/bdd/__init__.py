from chastack_bdd.tipos import *
from chastack_bdd.errores import *
from chastack_bdd.utiles import *

@runtime_checkable
class ProtocoloBaseDeDatos(Protocol):
    def DESCRIBE(self: Self, tabla :str) -> Self: ...
    def SELECT(self : Self, tabla : str, columnas : list[str], columnasSecundarias: Optional[dict[str, list[str]] ] = {}) -> Self:...
    def DELETE(self : Self, tabla : str) -> Self: ...
    def INSERT(self : Self, tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self: ...
    def UPDATE(self : Self, tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self: ...
    def WHERE(self : Self, tipoCondicion : TipoCondicion = TipoCondicion.IGUAL , **columnaValor : Unpack[dict[str, Any]]) -> Self: ...
    def JOIN(self : Self,   tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion : TipoUnion = TipoUnion.INNER) -> Self: ...
    def ORDER_BY(self, orden : [dict[str, TipoOrden]]): ...
    def LIMIT(self : Self, desplazamiento: int  , limite : int) -> Self: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type,excl_val,exc_tb) -> None: ...
    def ejecutar(self: Self) -> Self :...
    def devolverUnResultado(self: Self) -> Resultado :...
    def devolverResultados(self: Self) -> tuple[Resultado] :...
    def devolverIdUltimaInsercion(self:Self) -> Optional[int] :...

class InstruccionPrincipal():
    ''' 
        Clase que permite definir la clausula principal de una consulta SQL. 
        Altamente acoplada con la clase Consulta y dependiente de la misma.    
    '''

    _slots__ = \
    (
        '__instruccion'
    )
    @sobrecargar
    def __init__(self):
        self.__instruccion = ''
    
    @sobrecargar
    def __init__(self, consulta: str):
        self.__instruccion = consulta
    
    def chequearOcupado(self):
        if self.__instruccion: raise ErrorMalaSintaxisSQL("La clausula principal ya ha sido definida.")
    def esDescribe(self):
        self.__instruccion = 'DESCRIBE'
    def esInsert(self):
        self.__instruccion = 'INSERT'
    def esSelect(self):
        self.__instruccion = 'SELECT'
    def esDelete(self):
        self.__instruccion = 'DELETE'
    def esUpdate(self):
        self.__instruccion = 'UPDATE'
    def construirConsulta(self, parametrosPrincipales, condicion, union, orden,  limite):
        if not self.__instruccion: raise ErrorMalaSintaxisSQL("No se ha definido una clausula principal.")
        if self.__instruccion == 'INSERT':
            if condicion or union or limite: raise ErrorMalaSintaxisSQL("Las instrucciones INSERT no pueden tener clausulas WHERE, JOIN o LIMIT.")
        return self.__instruccion + '\n' + parametrosPrincipales + union + condicion + orden + limite + ';'


class Consulta():
    '''
    Clase que permite generar consultas SQL de forma programática. Las consultas se construyen concatenando
    las clausulas principales (SELECT, DELETE, INSERT, UPDATE) y las clausulas secundarias (WHERE, JOIN). Luego
    se espera que el objeto sea convertido a string para obtener la consulta SQL.


    METODOS PUBLICOS
    - SELECT(tabla : str, columnas : list[str] columnasSecundarias: Optional[Dict[str, List[str]] ] = {}) -> Self
    - DELETE(tabla : str) -> Self
    - INSERT(tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self
    - UPDATE(tabla : str, **asignaciones : Unpack[dict[str, Any]]) -> Self
    - WHERE(tipoCondicion : TipoCondicion = TipoCondicion.IGUAL , **columnaValor : Unpack[dict[str, Any]]) -> Self
    - JOIN(tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion : TipoUnion = TipoUnion.INNER) -> Self
    - LIMIT(desplazamiento: int  , limite : int) -> Self
    Aclaracion: Los metodos From, Set y LIMIT no son metodos publicos, ya que son llamados internamente por los metodos que invocan clausulas principales.

    ATRIBUTOS PUBLICOS
    - TipoCondicion: Enumeracion que contiene los tipos de condiciones posibles.
    - TipoUnion: Enumeracion que contiene los tipos de joins posibles.

    EJEMPLOS DE USO:


    > consulta = Consulta().SELECT(tabla='Usuarios', columnas=['nombreUsuario', 'correo']).WHERE(id=1).LIMIT(10, 5)
    > print(consulta)


    SELECT 
    Usuarios.nombreUsuario, Usuarios.correo
    FROM Usuarios
    WHERE Usuarios.id = 1
    LIMIT 10, 5
    ;

    > consulta = Consulta().DELETE(tabla='Usuarios').WHERE(id=1)
    > print(consulta)

    DELETE 
    FROM Usuarios
    WHERE Usuarios.PRIMARY_KEY != 'NULL'
    AND Usuarios.id = 1
    ;

    > consulta = Consulta().INSERT(tabla='Usuarios', nombreUsuario='Juan')

    > consulta = Consulta().SELECT(tabla='Usuarios', columnas=['nombreUsuario', 'correo'], columnasSecundarias={'Discos': 'autor'})
    > consulta.JOIN(tablaSecundaria='Discos', columnaPrincipal='esPremium', columnaSecundaria ='esPremium', tipoUnion=TipoUnion.INNER)
    > print(consulta)

    SELECT Usuarios.nombreUsuario, Usuarios.correo, Discos.a, Discos.u, Discos.t, Discos.o, Discos.r
    FROM Usuarios
    INNER JOIN Discos ON Usuarios.esPremium = Discos.esPremium
    ;

    CASOS DE ERROR:

    La clase levanta errores de tipo ErrorMalaSintaxisSQL en los siguientes casos:
    - Se intenta invocar una clausula principal (SELECT, DELETE, INSERT, UPDATE) más de una vez.
    - Se intenta convertir a string sin clausula principal
    - Se intenta pedir columnas secundarias de una tabla que no ha sido unida.

    La clase levanta errores de tipo ErrorMalaSolicitud en los siguientes casos:

    CASOS
    
    
    '''

    __slots__ = \
    (   '__parametros_principales',
        '__instruccionPrincipal',
        '__tabla_principal',
        '__tablas_secundarias',
        '__condicion',
        '__union',
        '__orden',
        '__limite',
        '__returning',
        )

    
    @sobrecargar
    def __init__(self):
        self.reiniciar()

    @sobrecargar
    def __init__(self,consulta : str):
        self.reiniciar()
        self.__instruccionPrincipal = InstruccionPrincipal(consulta)
        self.__parametros_principales = " "

    def SELECT(self, tabla : str, columnas : list[str], columnasSecundarias: Optional[dict[str, list[str]] ] = {}) -> Self:
        self.__tabla_principal = tabla
        self.__instruccionPrincipal.esSelect()
        self.__parametros_principales = self.etiquetar(tabla, columnas)
        for t2, c2 in columnasSecundarias.items():
            self.__tablas_secundarias[t2] = 0
            self.__parametros_principales += ', ' + self.etiquetar(t2, c2) 
        self.__parametros_principales += '\n'
        self.__FROM(tabla)
        return self
    def DESCRIBE(self: Self, tabla :str) -> Self:
        self.__tabla_principal = tabla
        self.__instruccionPrincipal.esDescribe()
        self.__parametros_principales += self.__tabla_principal
        return self
    def DELETE(self, tabla : str):
        self.__tabla_principal = tabla
        self.__instruccionPrincipal.esDelete()
        self.__FROM(tabla)
        self.WHERE(TipoCondicion.NO_ES, id = None)
        return self
    def INSERT(self, tabla : str, **asignaciones : Unpack[dict[str, Any]]):
        self.__tabla_principal = tabla
        self.__instruccionPrincipal.esInsert()
        self.__parametros_principales = 'INTO ' + tabla + '\n'
        self.__SET(**asignaciones)
        return self
    def UPDATE(self, tabla : str, **asignaciones : Unpack[dict[str, Any]]):
        self.__tabla_principal = tabla
        self.__instruccionPrincipal.esUpdate()
        self.__parametros_principales = tabla + '\n'
        self.__SET(**asignaciones)
        self.WHERE(TipoCondicion.NO_ES, id = None)
        return self
    def WHERE(self, tipoCondicion : TipoCondicion = TipoCondicion.IGUAL , **columnaValor : Unpack[dict[str, Any]]):
        condiciones : str = '   AND '.join(f"{self.etiquetar(self.__tabla_principal, [columna]) } {tipoCondicion} {self.adaptar(valor, parecido=tipoCondicion == TipoCondicion.PARECIDO)}" for columna, valor in columnaValor.items())
        if not condiciones: return self
        if not self.__condicion: self.__condicion = f'WHERE {condiciones}\n'
        else: self.__condicion += f' AND {condiciones}\n'
        return self
    def ORDER_BY(self, orden : [dict[str, TipoOrden]]):
        if not orden: return self
        orden : str = ', '.join(f"{self.etiquetar(self.__tabla_principal,[columna])} {direccion}" for columna, direccion in orden.items())        
        if not self.__orden: self.__orden = f'ORDER BY {orden}\n'
        else: self.__orden += f' , {orden}\n'
        return self

    def RETURNING_ID(self):
        self.__returning = True
    def JOIN(self, tablaSecundaria, columnaPrincipal, columnaSecundaria, tipoUnion : TipoUnion = TipoUnion.INNER):
        self.__tablas_secundarias[tablaSecundaria] = 1
        nuevoJoin : str = tipoUnion +  ' JOIN ' + tablaSecundaria + ' ON ' + self.etiquetar(self.__tabla_principal, [columnaPrincipal]) + ' = ' + self.etiquetar(tablaSecundaria, [columnaSecundaria]) + '\n'
        self.__union += nuevoJoin        
        return self
    
    def LIMIT(self, desplazamiento: int  , limite : int):
        if self.__limite : raise ErrorMalaSintaxisSQL("La clausula LIMIT ya ha sido definida.")
        self.__limite  =  'LIMIT ' + str(desplazamiento) + ', ' + str(limite) + '\n'
        return self
    def __FROM(self, tabla : str):
        self.__parametros_principales += 'FROM ' + tabla + '\n'
        return self
    def __SET(self, **columnaValor: Unpack[dict[str, Any]]):
        columnas = list(columnaValor.keys())
        valores = [self.adaptar(v) for v in columnaValor.values()]

        
        if str(self._Consulta__instruccionPrincipal._InstruccionPrincipal__instruccion) == 'INSERT':
            cols_sql = f"({', '.join(columnas)})"
            vals_sql = f"VALUES ({', '.join(valores)}) {' RETURNING id ' if self.__returning else ''}"
            self.__parametros_principales += f"{cols_sql}\n{vals_sql}\n"
        else:
            
            asignaciones = ', '.join(
                f"{col} = {val}"
                for col, val in zip(columnas, valores)
            )
            self.__parametros_principales += f"SET {asignaciones} {' RETURNING id ' if self.__returning else ''}\n"

        return self

    
    def etiquetar(self, tabla: str, columnas : list[str]) -> str:
        """Recibe una tabla y columnas. devuelve cada columna en el namespace de la tabla"""
        #return ", ".join(columnas)
        return ', '.join([tabla + '.' + columna  for columna in columnas])

    def adaptar(self, valor : Any, parecido : bool = False) -> str:
        return formatearValorParaSQL(valor, parecido=parecido)

    def reiniciar(self):
        self.__instruccionPrincipal = InstruccionPrincipal()
        self.__parametros_principales = ''
        self.__condicion = ''
        self.__union = ''
        self.__orden = ''
        self.__limite = ''
        self.__returning = False

        self.__tabla_principal = ''
        self.__tablas_secundarias = {}

    def __str__(self):
        if not self.__parametros_principales: raise ErrorMalaSintaxisSQL("No se ha definido una clausula principal.") 
        for tabla, valor in self.__tablas_secundarias.items():
            if valor == 0:
                raise ErrorMalaSintaxisSQL(f"La tabla {tabla} no ha sido unida.")
        return self.__instruccionPrincipal.construirConsulta(self.__parametros_principales, self.__condicion, self.__union, self.__orden, self.__limite)
        




from chastack_bdd.bdd.mysql import ConfigMySQL, BaseDeDatos_MySQL
from chastack_bdd.bdd.postgresql import ConfigPostgreSQL, BaseDeDatos_PostgreSQL