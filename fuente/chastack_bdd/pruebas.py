import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ConfigMySQL, BaseDeDatos_MySQL  
from chastack_bdd.tabla import Tabla  
from chastack_bdd.registro import Registro

class Administrador(metaclass=Tabla):
    ...

config = ConfigMySQL(
        "localhost", 
        "servidor_local", 
        "Servidor!1234", 
        "fundacionzaffaroni_ar_desarrollo",
    )
bdd = BaseDeDatos_MySQL(config)



dds = Administrador.devolverRegistros(bdd, cantidad = 25, orden ={"id" : TipoOrden.DESC})
for dd in dds:
    print(dd)
    print(dd.nombre_usuario)
    print(dd.__slots__)
    print(dd.tabla)

from datetime import datetime
u = datetime.now().microsecond
admin1 = Administrador(bdd, dict(nombre="Admin",nombre_usuario=f"admin{u}",contrasena="admin1234".encode('utf-8'),correo=f"admin{u}@fundacionzaffaroni.ar"))
admin1.guardar()
print(Administrador)
print(admin1.id)

admin10 = Administrador(bdd=bdd,id=10)
print(admin10)
