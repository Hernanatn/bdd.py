import unittest
from chastack_bdd.bdd import ConfigPostgreSQL, BaseDeDatos_PostgreSQL
from chastack_bdd.tabla import Tabla, TablaIntermedia
from chastack_bdd.usuario import Usuario
from chastack_bdd.tipos import TipoOrden
from datetime import datetime
from sobrecargar import sobrecargar
import psycopg
import os
import traceback

ROOT_P: str = os.environ.get('PG_ROOT_PASSWORD')

def crearBaseDeDatos():
    with psycopg.connect(
        host="localhost",
        user="postgres",
        password=ROOT_P,
        dbname="postgres",
        autocommit=True
    ) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("CREATE DATABASE chastack_bdd_pruebas;")
            except psycopg.errors.DuplicateDatabase:
                pass

            cur.execute("DROP ROLE IF EXISTS usuario_de_prueba;")
            cur.execute("""
                CREATE ROLE usuario_de_prueba
                LOGIN PASSWORD 'pRU3b4s!1?2@3$4';
            """)
            cur.execute("GRANT CONNECT ON DATABASE chastack_bdd_pruebas TO usuario_de_prueba;")

    # Ahora conectar a la base creada para asignar permisos sobre esquema
    with psycopg.connect(
        host="localhost",
        user="postgres",
        password=ROOT_P,
        dbname="chastack_bdd_pruebas",
        autocommit=True
    ) as conn:
        with conn.cursor() as cur:
            # Conceder uso del esquema público
            cur.execute("GRANT USAGE ON SCHEMA public TO usuario_de_prueba;")

            # Conceder permisos sobre todas las tablas actuales en public
            cur.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO usuario_de_prueba;")

            # Conceder permisos sobre secuencias para evitar problemas con serial/autoincrement
            cur.execute("GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO usuario_de_prueba;")

            # Configurar para que futuras tablas y secuencias tengan estos permisos por defecto
            cur.execute("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO usuario_de_prueba;
            """)
            cur.execute("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                GRANT USAGE ON SEQUENCES TO usuario_de_prueba;
            """)

    print("[PostgreSQL]\t\tBase de datos y usuario creados con éxito.")
def crearYPoblarTablas():
    with psycopg.connect(
        host="localhost",
        user="postgres",
        password=ROOT_P,
        dbname="chastack_bdd_pruebas"
    ) as conn:
        cur = conn.cursor()

        # Crear tipo ENUM para Administrador.rol
        cur.execute("DROP TYPE IF EXISTS TipoRol CASCADE;")
        cur.execute("""
            CREATE TYPE TipoRol AS ENUM ('USUARIO','ADMINISTRADOR','SUPERUSUARIO');
        """)

        # Tablas adaptadas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Cliente(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                nombre VARCHAR(150) NOT NULL,
                apellido VARCHAR(150) NOT NULL,
                edad INTEGER NOT NULL,
                correo VARCHAR(150) NOT NULL,
                bio TEXT NOT NULL,
                url_img_principal VARCHAR(150)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Nota(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                titulo VARCHAR(150) NOT NULL,
                subtitulo VARCHAR(150) NOT NULL,
                cuerpo TEXT NOT NULL,
                resumen VARCHAR(250),
                url_img_principal VARCHAR(150)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Tema(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                nombre VARCHAR(150) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Voz(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                voz VARCHAR(150) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS TemaDeNota(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                id_tema INTEGER NOT NULL REFERENCES Tema(id) ON DELETE CASCADE,
                id_nota INTEGER NOT NULL REFERENCES Nota(id) ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS VozDeNota(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                id_voz INTEGER NOT NULL REFERENCES Voz(id) ON DELETE CASCADE,
                id_nota INTEGER NOT NULL REFERENCES Nota(id) ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Administrador(
                id SERIAL PRIMARY KEY,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                nombre VARCHAR(50) DEFAULT NULL,
                nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
                correo VARCHAR(75) NOT NULL UNIQUE,
                contrasena BYTEA NOT NULL,
                sal BYTEA NOT NULL,
                rol TipoRol DEFAULT 'USUARIO' NOT NULL,
                fecha_ultimo_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                id_sesion VARCHAR(300) UNIQUE,
                codigo_unico VARCHAR(300) DEFAULT NULL
            );
        """)

        conn.commit()
        print("[PostgreSQL]\tTodas las tablas se han creado correctamente.")

    # Poblar datos
    with psycopg.connect(
        host="localhost",
        user="usuario_de_prueba",
        password="pRU3b4s!1?2@3$4",
        dbname="chastack_bdd_pruebas"
    ) as conn:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Tema (nombre) VALUES
            ('Salud Pública'),
            ('Educación Rural'),
            ('Infraestructura'),
            ('Acceso a Medicamentos'),
            ('Cultura Local');
        """)

        cur.execute("""
            INSERT INTO Nota (titulo, subtitulo, cuerpo, resumen, url_img_principal) VALUES
            ('La salud en zonas rurales', 'Un desafío persistente', 'Texto extenso sobre salud rural...', 'Panorama de la salud rural', 'img/salud1.jpg'),
            ('Educación en parajes', 'Desigualdad educativa', 'Texto sobre educación...', 'Educación rural en cifras', 'img/edu1.jpg'),
            ('Medicamentos esenciales', 'Acceso limitado', 'Texto sobre acceso a medicamentos...', 'El acceso a los medicamentos esenciales', 'img/med1.jpg'),
            ('El rol del médico rural', 'Historias de vocación', 'Texto con entrevistas a médicos...', 'Testimonios rurales', 'img/medico1.jpg'),
            ('Cultura y salud', 'Interculturalidad médica', 'Texto sobre medicina y cultura...', 'Cruce entre saberes', 'img/cultura1.jpg');
        """)

        cur.execute("""
            INSERT INTO TemaDeNota (id_tema, id_nota) VALUES
            (1, 1), (2, 2), (4, 3), (1, 4), (5, 5);
        """)

        cur.execute("""
            INSERT INTO Voz (voz) VALUES
            ('Dr. Fernández'),
            ('Enfermera María'),
            ('Docente rural Juan'),
            ('Vecina Marta'),
            ('Promotor de salud Pablo');
        """)

        cur.execute("""
            INSERT INTO VozDeNota (id_voz, id_nota) VALUES
            (1, 1), (2, 1), (3, 2), (4, 4), (5, 5);
        """)

        # Para las contraseñas y sales simulamos hashes binarios
        cur.execute("""
            INSERT INTO Administrador (nombre, nombre_usuario, contrasena, sal, correo) VALUES
            ('Ana Pérez', 'admin1', decode(md5('admin1'), 'hex'), decode(md5('sal1'), 'hex'), 'admin1@mail.com'),
            ('Luis Gómez', 'admin2', decode(md5('admin2'), 'hex'), decode(md5('sal2'), 'hex'), 'admin2@mail.com'),
            ('Sofía Ríos', 'admin3', decode(md5('admin3'), 'hex'), decode(md5('sal3'), 'hex'), 'admin3@mail.com'),
            ('Carlos Díaz', 'admin4', decode(md5('admin4'), 'hex'), decode(md5('sal4'), 'hex'), 'admin4@mail.com'),
            ('Elena Ruiz', 'admin5', decode(md5('admin5'), 'hex'), decode(md5('sal5'), 'hex'), 'admin5@mail.com');
        """)

        conn.commit()
        print("[PostgreSQL]\t\t¡Inserciones completadas con éxito!")
def destruirBaseDeDatos():
    with psycopg.connect(
        host="localhost",
        user="postgres",
        password=ROOT_P,
        dbname="postgres"
    ) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS chastack_bdd_pruebas;")
        cur.execute("DROP ROLE IF EXISTS usuario_de_prueba;")
        print("[PostgreSQL]\t\tBase de datos y usuario eliminados con éxito.")

CONFIG_BDD_PRUEBAS = ConfigPostgreSQL(
    "localhost",
    "usuario_de_prueba",
    "pRU3b4s!1?2@3$4",
    "chastack_bdd_pruebas",
)

class Cliente(metaclass=Tabla): ...
class Administrador(Usuario, metaclass=Tabla):
    @sobrecargar
    def unMetodo(x: int): ...
    @sobrecargar
    def unMetodo(x: str): ...

class PruebaRegistros_PostgreSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_PostgreSQL(CONFIG_BDD_PRUEBAS)
    def test_crear_registro(self):
        cliente = Cliente(self.bdd,
        {
            'nombre': "Juan",
            'apellido': "Pelotas",
            'correo': "juan_pelotas@gmail.com",
            'edad': 70,
            "bio": 'una biografia aleatoria\nde juan pelotas.',
        })
        cliente.guardar()
        print(cliente)
        self.assertIsNotNone(cliente.id)
        self.assertEqual(cliente.id,1)
        u = datetime.now().microsecond
        admin = Administrador(
            self.bdd,
            dict(
                nombre="Admin",
                nombre_usuario=f"admin{u}",
                contrasena="admin1234".encode('utf-8'),
                sal="asdadas".encode('utf-8'),
                rol=Usuario.TipoRol.SUPERUSUARIO,
                correo=f"admin{u}@fundacionzaffaroni.ar"
            )
        )
        admin.guardar()
        print(admin)
        self.assertIsNotNone(admin.id)
        self.assertEqual(admin.nombre, "Admin")
        self.assertEqual(admin.rol, Usuario.TipoRol.SUPERUSUARIO)
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.SUPERUSUARIO))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.ADMINISTRADOR))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.USUARIO))

class PruebaUsuario_PostgreSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_PostgreSQL(CONFIG_BDD_PRUEBAS)

    def test_devolver_administradores(self):
        admins = Administrador.devolverRegistros(
            self.bdd, cantidad=25, orden={"id": TipoOrden.DESC},
            correo="desarrollo@cajadeideas.ar"
        )
        self.assertIsInstance(admins, (list, tuple))
        for admin in admins:
            self.assertTrue(hasattr(admin, "nombre_usuario"))

    def test_registro_y_login_usuario(self):
        u = datetime.now().microsecond
        juan = Administrador.registrar(
            self.bdd,
            correo=f"juan@juan.juan{u}",
            contrasena="JuanJuan!1234",
            atributo_juan=7,
            rol=Usuario.TipoRol.USUARIO,
            nombre="juan"
        )
        self.assertIsNotNone(juan)
        juan.guardar()
        print(juan)
        self.assertIsNotNone(juan.id)
        juan2 = juan.ingresar(self.bdd, f"juan@juan.juan{u}", "JuanJuan!1234")
        self.assertEqual(juan2.correo, f"juan@juan.juan{u}")
        self.assertEqual(juan2.rol, Usuario.TipoRol.USUARIO)
        self.assertFalse(juan2.verificarRol(Usuario.TipoRol.SUPERUSUARIO))
        self.assertFalse(juan2.verificarRol(Usuario.TipoRol.ADMINISTRADOR))
        self.assertTrue(juan2.verificarRol(Usuario.TipoRol.USUARIO))

    def test_crear_administrador(self):
        u = datetime.now().microsecond
        admin = Administrador(
            self.bdd,
            dict(
                nombre="Admin",
                nombre_usuario=f"admin{u}",
                contrasena="admin1234".encode('utf-8'),
                sal="asdadas".encode('utf-8'),
                rol=Usuario.TipoRol.ADMINISTRADOR,
                correo=f"admin{u}@fundacionzaffaroni.ar"
            )
        )
        admin.guardar()
        print(admin)
        self.assertIsNotNone(admin.id)
        self.assertEqual(admin.nombre, "Admin")
        self.assertEqual(admin.rol, Usuario.TipoRol.ADMINISTRADOR)
        self.assertFalse(admin.verificarRol(Usuario.TipoRol.SUPERUSUARIO))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.ADMINISTRADOR))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.USUARIO))



class Nota(metaclass=Tabla): ...
class Voz(metaclass=Tabla): ...
class VozDeNota(metaclass=TablaIntermedia):
    tabla_primaria = Nota
    tabla_secundaria = Voz

class Nota(metaclass=Tabla):
    muchosAMuchos = {Voz: VozDeNota}
    def añadirVoz(self, voz):
        self.añadirRelacion(voz, Voz)
    def obtenerVoces(self):
        return self.obtenerMuchos(Voz)
    def borrarVoz(self, voz: Voz):
        self.borrarRelacion(voz, Voz)

class PruebaTablaIntermedia_PostgreSQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_PostgreSQL(CONFIG_BDD_PRUEBAS)
    def test_relacion_entre_nota_y_voces(self):
        notas = Nota.devolverRegistros(self.bdd, cantidad=25, orden={"id": TipoOrden.DESC})
        self.assertGreater(len(notas), 0)

        nota = Nota(self.bdd, id=notas[0].id)
        voces = Voz.devolverRegistros(self.bdd)
        self.assertGreaterEqual(len(voces), 3)

        # Añadir voces
        nota.añadirVoz(voces[0])
        nota.añadirVoz(voces[1])
        nota.añadirVoz(Voz(self.bdd, id=voces[2].id))
        nota.guardar()
        print(nota)
        self.assertIsNotNone(nota.id)
        obtenidas = nota.obtenerVoces()
        self.assertGreaterEqual(len(obtenidas), 3)

        # Borrar una voz
        for _, voz in obtenidas.items():
            nota.borrarVoz(voz)
            break
        nota.guardar()
        print(nota)
        self.assertIsNotNone(nota.id)
        nota_recargada = Nota(self.bdd, id=nota.id)
        self.assertIsInstance(nota_recargada, Nota)



if __name__ == "__main__":
    try:
        crearBaseDeDatos()
        crearYPoblarTablas()
        unittest.main()
    finally:
        destruirBaseDeDatos()
