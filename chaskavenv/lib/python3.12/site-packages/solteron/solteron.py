"""
===============
solteron.py
===============
Patrón 'Singleton' en Python 3.

* Repositorio del proyecto: https://github.com/Hernanatn/solteron.py
* Documentación: https://github.com/Hernanatn/solteron.py/blob/master/README.MD

Derechos de autor (c) 2023 Hernán A. Teszkiewicz Novick. Distribuído bajo licencia MIT.
Hernan ATN | herni@cajadeideas.ar 
"""

__author__ = "Hernan ATN"
__copyright__ = "(c) 2023, Hernán A. Teszkiewicz Novick."
__license__ = "MIT"
__version__ = "0.1.5"
__email__ = "herni@cajadeideas.ar"

__all__ = ['Solteron', 'Singleton']

from typing import Any

class Solteron(type):
    __instancias : dict [type,Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instancias:
            cls.__instancias[cls] = super(Solteron, cls).__call__(*args, **kwargs)
        return cls.__instancias[cls]

Singleton = Solteron

if __name__ == '__main__':
    print(__doc__)