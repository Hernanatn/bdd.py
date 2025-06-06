


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



nota = Nota.devolverRegistros(bdd, cantidad = 25, orden ={"id" : TipoOrden.DESC})[0]
nota = Nota(bdd, id=nota.id)
print(nota.obtenerVoces())

voces = Voz.devolverRegistros(bdd)
voz = voces[0]
nota.añadirVoz(voz)
nota.añadirVoz(voces[1])
nota.añadirVoz(Voz(bdd, voces[2].id))
nota.guardar()
print(nota.obtenerVoces())
nota.borrarVoz(voz)
nota.guardar()
print(nota.obtenerVoces())
nota = Nota(bdd, id=nota.id)
print(nota.obtenerVoces())
