import unittest
from chastack_bdd.bdd import ConfigMySQL, BaseDeDatos_MySQL
from chastack_bdd.tabla import Tabla, TablaIntermedia
from chastack_bdd.usuario import Usuario
from chastack_bdd.tipos import TipoOrden
from datetime import datetime
from sobrecargar import sobrecargar
import mysql.connector
from mysql.connector import errorcode, Error
import os
import traceback

CI = os.environ.get("CI", "false").lower() == "true"
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1") if CI else "localhost"
ROOT_P : str = os.environ.get('MYSQL_ROOT_PASSWORD')



def crearBaseDeDatos():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user="root",
        password=ROOT_P  
    )
    try:
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS `chastack_bdd_pruebas`;")

        cursor.execute("""
            CREATE USER IF NOT EXISTS 'usuario_de_prueba'@'%'
            IDENTIFIED BY 'pRU3b4s!1?2@3$4';
        """)

        privilegios = ['SELECT', 'UPDATE', 'DELETE', 'INSERT', 'EXECUTE']
        for priv in privilegios:
            cursor.execute(f"""
                GRANT {priv} ON chastack_bdd_pruebas.* TO 'usuario_de_prueba'@'%';
            """)

        cursor.execute("FLUSH PRIVILEGES;")
        #print("Base de datos y usuario creados con éxito.")
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def crearYPoblarTablas():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=ROOT_P,  # Reemplazar
        database="chastack_bdd_pruebas"
    )
    try:
        cursor = conn.cursor()

        # Tabla Cliente
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Cliente (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                nombre VARCHAR(150) NOT NULL,
                apellido VARCHAR(150) NOT NULL,
                edad int NOT NULL,
                correo VARCHAR(150) NOT NULL,
                bio TEXT NOT NULL,
                url_img_principal VARCHAR(150)
            );
        """)

        # Tabla Nota
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Nota (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                titulo VARCHAR(150) NOT NULL,
                subtitulo VARCHAR(150) NOT NULL,
                cuerpo TEXT NOT NULL,
                resumen VARCHAR(250),
                url_img_principal VARCHAR(150)
            );
        """)

        # Tabla Tema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tema (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                nombre VARCHAR(150) NOT NULL
            );
        """)

        # Tabla Voz
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Voz (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                voz VARCHAR(150) NOT NULL
            );
        """)

        # Tabla TemaDeNota
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TemaDeNota (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                id_tema INT NOT NULL,
                id_nota INT NOT NULL,
                FOREIGN KEY (id_tema) REFERENCES Tema(id) ON DELETE CASCADE,
                FOREIGN KEY (id_nota) REFERENCES Nota(id) ON DELETE CASCADE
            );
        """)

        # Tabla VozDeNota
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS VozDeNota (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                id_voz INT NOT NULL,
                id_nota INT NOT NULL,
                FOREIGN KEY (id_voz) REFERENCES Voz(id) ON DELETE CASCADE,
                FOREIGN KEY (id_nota) REFERENCES Nota(id) ON DELETE CASCADE
            );
        """)

        # Tabla Permiso
        # // cursor.execute("""
        # //     CREATE TABLE IF NOT EXISTS Permiso (
        # //         id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        # //         fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        # //         fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        # //         rol VARCHAR(25)
        # //     );
        # // """)

        # Tabla Administrador (unificada con campos de Usuario)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Administrador (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                nombre VARCHAR(50) DEFAULT NULL,
                nombre_usuario VARCHAR(50) NOT NULL,
                correo VARCHAR(75) NOT NULL,
                contrasena VARBINARY(96) NOT NULL,
                sal VARBINARY(96) NOT NULL,
                rol ENUM('USUARIO','ADMINISTRADOR','SUPERUSUARIO') DEFAULT 'USUARIO' NOT NULL,
                fecha_ultimo_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                id_sesion VARCHAR(300) DEFAULT NULL,
                codigo_unico VARCHAR(300) DEFAULT NULL,
                UNIQUE KEY(nombre_usuario),
                UNIQUE KEY(correo),
                UNIQUE KEY(id_sesion)
            );
        """)

        # Tabla PermisosDeAdministrador
        ## cursor.execute("""
        ##     CREATE TABLE IF NOT EXISTS PermisosDeAdministrador (
        ##         id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        ##         fecha_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ##         fecha_modificacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        ##         id_administrador INT NOT NULL,
        ##         id_permiso INT NOT NULL,
        ##         CONSTRAINT PermisosDeAdministrador_ibfk_1 FOREIGN KEY (id_administrador) REFERENCES Administrador(id) ON DELETE CASCADE,
        ##         CONSTRAINT PermisosDeAdministrador_ibfk_2 FOREIGN KEY (id_permiso) REFERENCES Permiso(id) ON DELETE CASCADE,
        ##         UNIQUE KEY(administrador_permiso) (id_administrador, id_permiso)
        ##     );
        ## """)

        conn.commit()
        #print("Todas las tablas se han creado correctamente.")

    except Error as e:
        print("Error al crear las tablas:", e, '\n', traceback.format_exc())
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    
    conn = mysql.connector.connect(
        host="localhost",
        user="usuario_de_prueba",
        password="pRU3b4s!1?2@3$4",
        database="chastack_bdd_pruebas"
    )
    try:
        cursor = conn.cursor()

        # Inserciones en orden lógico
        cursor.execute("""
            INSERT INTO Tema (nombre) VALUES 
            ('Salud Pública'),
            ('Educación Rural'),
            ('Infraestructura'),
            ('Acceso a Medicamentos'),
            ('Cultura Local');
        """)

        cursor.execute("""
            INSERT INTO Nota (titulo, subtitulo, cuerpo, resumen, url_img_principal) VALUES 
            ('La salud en zonas rurales', 'Un desafío persistente', 'Texto extenso sobre salud rural...', 'Panorama de la salud rural', 'img/salud1.jpg'),
            ('Educación en parajes', 'Desigualdad educativa', 'Texto sobre educación...', 'Educación rural en cifras', 'img/edu1.jpg'),
            ('Medicamentos esenciales', 'Acceso limitado', 'Texto sobre acceso a medicamentos...', 'El acceso a los medicamentos esenciales', 'img/med1.jpg'),
            ('El rol del médico rural', 'Historias de vocación', 'Texto con entrevistas a médicos...', 'Testimonios rurales', 'img/medico1.jpg'),
            ('Cultura y salud', 'Interculturalidad médica', 'Texto sobre medicina y cultura...', 'Cruce entre saberes', 'img/cultura1.jpg');
        """)

        cursor.execute("""
            INSERT INTO TemaDeNota (id_tema, id_nota) VALUES 
            (1, 1), (2, 2), (4, 3), (1, 4), (5, 5);
        """)

        cursor.execute("""
            INSERT INTO Voz (voz) VALUES 
            ('Dr. Fernández'),
            ('Enfermera María'),
            ('Docente rural Juan'),
            ('Vecina Marta'),
            ('Promotor de salud Pablo');
        """)

        cursor.execute("""
            INSERT INTO VozDeNota (id_voz, id_nota) VALUES 
            (1, 1), (2, 1), (3, 2), (4, 4), (5, 5);
        """)


        cursor.execute("""
            INSERT INTO Administrador (nombre, nombre_usuario, contrasena, sal, correo) VALUES 
            ('Ana Pérez', 'admin1', UNHEX(SHA2('admin1',512)), UNHEX(SHA2('sal1',512)), 'admin1@mail.com'),
            ('Luis Gómez', 'admin2', UNHEX(SHA2('admin2',512)), UNHEX(SHA2('sal2',512)), 'admin2@mail.com'),
            ('Sofía Ríos', 'admin3', UNHEX(SHA2('admin3',512)), UNHEX(SHA2('sal3',512)), 'admin3@mail.com'),
            ('Carlos Díaz', 'admin4', UNHEX(SHA2('admin4',512)), UNHEX(SHA2('sal4',512)), 'admin4@mail.com'),
            ('Elena Ruiz', 'admin5', UNHEX(SHA2('admin5',512)), UNHEX(SHA2('sal5',512)), 'admin5@mail.com');
        """)

        # //cursor.execute("""
        # //    INSERT INTO Permiso (rol) VALUES 
        # //    ('superadmin'),
        # //    ('editor'),
        # //    ('moderador'),
        # //    ('analista'),
        # //    ('auditor');
        # //""")

        # //cursor.execute("""
        # //    INSERT INTO PermisosDeAdministrador (id_administrador, id_permiso) VALUES 
        # //    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5);
        # //""")

        conn.commit()
        #print("¡Inserciones completadas con éxito!")

    except Error as e:
        print(f"Error al conectar o insertar:", e, '\n', traceback.format_exc())
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def destruirBaseDeDatos():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=ROOT_P  
    )
    try:
        cursor = conn.cursor()

        cursor.execute("DROP DATABASE IF EXISTS `chastack_bdd_pruebas`;")
        cursor.execute("DROP USER IF EXISTS 'usuario_de_prueba'@'localhost';")
        cursor.execute("FLUSH PRIVILEGES;")
        #print("Base de datos y usuario eliminados con éxito.")
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

CONFIG_BDD_PRUEBAS = ConfigMySQL(
            "localhost",
            "usuario_de_prueba",
            "pRU3b4s!1?2@3$4",
            "chastack_bdd_pruebas",
        )

class Cliente(metaclass=Tabla):...

class PruebaRegistros(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_MySQL(CONFIG_BDD_PRUEBAS)

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
        #print(cliente)
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
        #print(admin)
        self.assertIsNotNone(admin.id)
        self.assertEqual(admin.nombre, "Admin")
        self.assertEqual(admin.rol, Usuario.TipoRol.SUPERUSUARIO)
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.SUPERUSUARIO))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.ADMINISTRADOR))
        self.assertTrue(admin.verificarRol(Usuario.TipoRol.USUARIO))

class Administrador(Usuario,metaclass=Tabla):
    @sobrecargar
    def unMetodo(x: int): ...

    @sobrecargar
    def unMetodo(x: str): ...

class PruebaUsuario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_MySQL(CONFIG_BDD_PRUEBAS)

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
        #print(juan)
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
        #print(admin)
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


class PruebaTablaIntermedia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bdd = BaseDeDatos_MySQL(CONFIG_BDD_PRUEBAS)

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
        #print(nota)
        self.assertIsNotNone(nota.id)
        obtenidas = nota.obtenerVoces()
        self.assertGreaterEqual(len(obtenidas), 3)

        # Borrar una voz
        for _, voz in obtenidas.items():
            nota.borrarVoz(voz)
            break
        nota.guardar()
        #print(nota)
        self.assertIsNotNone(nota.id)
        nota_recargada = Nota(self.bdd, id=nota.id)
        self.assertIsInstance(nota_recargada, Nota)

# REFACTORIZAR: (Hernán) Segregar pruebas en submódulos.
if __name__ == "__main__":
    try:
        crearBaseDeDatos()
        crearYPoblarTablas()
        unittest.main()
    finally:
        destruirBaseDeDatos()