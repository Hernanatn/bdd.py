import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ConfigMySQL, BaseDeDatos_MySQL  
from chastack_bdd.tabla import Tabla  
from chastack_bdd.registro import Registro

class Discos(metaclass=Tabla):
    def devolverArtista(self):
        return self.idAutor


config = ConfigMySQL("localhost", "servidor_local", "Servidor!1234", "BaseDePrueba")
bdd = BaseDeDatos_MySQL(config)

disco1 = Discos(bdd=bdd,id=2)


print(disco1.tabla)
print(disco1.id)
print(disco1.tipo.haciaCadena())
print(disco1.soporte)
print(disco1.devolverArtista())

disco2 = Discos(bdd=bdd,id=5)


print(disco2.tabla)
print(disco2.id)
print(disco2.tipo.haciaCadena())
print(disco2.soporte)
print(disco2.devolverArtista())

print(f"{Discos.TipoSoporte.desdeCadena("DIGITAL").value=}")

dds = Discos.devolverRegistros(bdd, cantidad = 25, orden ={"id" : TipoOrden.DESC})
for dd in dds:

    print(dd.tabla)
    print(dd.id)
    print(dd.tipo.haciaCadena())

