


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ConfigMySQL, BaseDeDatos_MySQL, ProtocoloBaseDeDatos
from chastack_bdd.tabla import Tabla , TablaIntermedia

##### PRUEBAS  TABLA INTERMEDIA ####



class Nota(metaclass=Tabla): ...
class Voz(metaclass=Tabla): ...
   
class VozDeNota(metaclass = TablaIntermedia):
    tabla_primaria  = Nota 
    tabla_secundaria = Voz

class Nota(metaclass=Tabla):
    muchosAMuchos = {Voz : VozDeNota}

    def añadirVoz(self, voz):
        self.añadirRelacion(voz, Voz)

    def obtenerVoces(self):
        return self.obtenerMuchos(Voz)
    
    def borrarVoz(self, voz: Voz):
        self.borrarRelacion(voz, Voz)

config = ConfigMySQL(
        "localhost", 
        "servidor_local", 
        "Servidor!1234", 
        "fundacionzaffaroni_ar_desarrollo",
    )
bdd = BaseDeDatos_MySQL(config)



notas = Nota.devolverRegistros(bdd, cantidad = 25, orden ={"id" : TipoOrden.DESC})
print(notas)

for nota in notas:
    print(nota)
    nota = Nota(bdd, id=nota.id)
    print(nota)

    voces = Voz.devolverRegistros(bdd)
    voz = voces[0]
    nota.añadirVoz(voz)
    nota.añadirVoz(voces[1])
    nota.añadirVoz(Voz(bdd, voces[2].id))
    nota.guardar()

    print(nota)
    for _,voz in nota.obtenerVoces().items(): print(voz)
    nota.borrarVoz(voz)
    nota.guardar()
    print(nota)
    for _,voz in nota.obtenerVoces().items(): print(voz)
    nota = Nota(bdd, id=nota.id)
    print(nota)
    for _,voz in nota.obtenerVoces().items(): print(voz)
