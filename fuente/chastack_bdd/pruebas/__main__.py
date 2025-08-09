import unittest
from chastack_bdd.pruebas import pruebas_mysql, pruebas_postgresql,implementaciones

if __name__ == "__main__":
    try:
        

        pruebas_mysql.destruirBaseDeDatos()
        pruebas_mysql.crearBaseDeDatos()
        pruebas_mysql.crearYPoblarTablas()

        pruebas_postgresql.destruirBaseDeDatos()
        pruebas_postgresql.crearBaseDeDatos()
        pruebas_postgresql.crearYPoblarTablas()

    
        from chastack_bdd.pruebas.pruebas_mysql import *
        from chastack_bdd.pruebas.pruebas_postgresql import *
        unittest.main(verbosity=0)
    finally:
        try:
            pruebas_mysql.destruirBaseDeDatos()
        except Exception as e:
            print("[ADVERTENCIA] Error destruyendo MySQL:", e)

        try:
            pruebas_postgresql.destruirBaseDeDatos()
        except Exception as e:
            print("[ADVERTENCIA] Error destruyendo PostgreSQL:", e)
