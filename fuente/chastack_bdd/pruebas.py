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
disco = Discos(bdd=bdd,id=2)

#print(disco.nombreUsuario)
print(disco.tabla)
print(disco.id)
print(disco.tipo.haciaCadena())
print(disco.soporte)
print(disco.devolverArtista())

print(f"{Discos.TipoSoporte.desdeCadena("DIGITAL").value=}")

