from chastack_bdd.bdd import (
    ConfigMySQL, BaseDeDatos_MySQL,
    ConfigPostgreSQL, BaseDeDatos_PostgreSQL
)
from pprint import pprint

MYSQL_CONFIG = ConfigMySQL(
    "localhost",
    "usuario_de_prueba",
    "pRU3b4s!1?2@3$4",
    "chastack_bdd_pruebas"
)

PG_CONFIG = ConfigPostgreSQL(
    "localhost",
    "usuario_de_prueba",
    "pRU3b4s!1?2@3$4",
    "chastack_bdd_pruebas"
)

def normalizar_tipo(tipo_str):
    """Homogeneiza nombres de tipos para comparaciones entre MySQL y PostgreSQL"""
    if not tipo_str:
        return ""
    t = tipo_str.lower()
    reemplazos = {
        "character varying": "varchar",
        "integer": "int",
        "double precision": "double",
        "timestamp without time zone": "timestamp",
        "boolean": "tinyint(1)",
    }
    for k, v in reemplazos.items():
        if t.startswith(k):
            return t.replace(k, v)
    return t

def comparar_describe(tabla):
    with BaseDeDatos_MySQL(MYSQL_CONFIG) as bdd_mysql, \
         BaseDeDatos_PostgreSQL(PG_CONFIG) as bdd_pg:
        
        describe_mysql = bdd_mysql.DESCRIBE(tabla).ejecutar().devolverResultados()
        describe_pg = bdd_pg.DESCRIBE(tabla).ejecutar().devolverResultados()

    # Normalizar tipos y ordenar por nombre de campo
    norm_mysql = [
        {**col, "Type": normalizar_tipo(col["Type"])} for col in describe_mysql
    ]
    norm_pg = [
        {**col, "Type": normalizar_tipo(col["Type"])} for col in describe_pg
    ]

    # Comparación
    iguales = True
    for col_mysql, col_pg in zip(norm_mysql, norm_pg):
        for campo in ("Field", "Type", "Key", "Null"):
            if str(col_mysql[campo]).lower() != str(col_pg[campo]).lower():
                print(f"[DIFF] {tabla}.{campo}: MySQL={col_mysql[campo]} | PG={col_pg[campo]}")
                iguales = False
    return iguales

def comparar_datos(tabla):
    with BaseDeDatos_MySQL(MYSQL_CONFIG) as bdd_mysql, \
         BaseDeDatos_PostgreSQL(PG_CONFIG) as bdd_pg:
        
        datos_mysql = bdd_mysql.SELECT(tabla, ["*"]).ejecutar().devolverResultados() or []
        datos_pg = bdd_pg.SELECT(tabla, ["*"]).ejecutar().devolverResultados() or []

    if len(datos_mysql) != len(datos_pg):
        print(f"[DIFF] Cantidad de filas en {tabla}: MySQL={len(datos_mysql)} | PG={len(datos_pg)}")
        return False
    
    # Comparar fila a fila (ignorando pequeñas diferencias de formato en fechas)
    iguales = True
    for fila_mysql, fila_pg in zip(datos_mysql, datos_pg):
        for k in fila_mysql.keys():
            vm, vp = fila_mysql[k], fila_pg[k]
            if isinstance(vm, str) and isinstance(vp, str):
                if vm.strip() != vp.strip():
                    print(f"[DIFF] {tabla}.{k}: MySQL={vm} | PG={vp}")
                    iguales = False
            elif vm != vp:
                print(f"[DIFF] {tabla}.{k}: MySQL={vm} | PG={vp}")
                iguales = False
    return iguales

if __name__ == "__main__":
    tablas = ["cliente", "nota", "tema", "voz", "temadenota", "vozdenota", "administrador"]
    print("Comparando DESCRIBE...")
    for t in tablas:
        ok = comparar_describe(t)
        print(f"  {t}: {'OK' if ok else 'DIFERENCIAS'}")

    print("\nComparando datos...")
    for t in tablas:
        ok = comparar_datos(t)
        print(f"  {t}: {'OK' if ok else 'DIFERENCIAS'}")
