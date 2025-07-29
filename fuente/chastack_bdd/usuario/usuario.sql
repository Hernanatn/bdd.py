CREATE TABLE IF NOT EXISTS `Usuario` (
    `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT
    , `fecha_carga` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    , `fecha_modificacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    --
    , `nombre_usuario` varchar(50) NOT NULL
    , `correo` varchar(75) NOT NULL
    , `contrasena` varbinary(96) NOT NULL
    , `fecha_ultimo_ingreso` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    , `id_sesion` varchar(300) DEFAULT NULL
    , `codigo_unico` varchar(300) DEFAULT NULL
    , `sal` varbinary(96) NOT NULL
    , `rol` ENUM('USUARIO','ADMINISTRADOR','SUPERUSUARIO') DEFAULT 'USUARIO' NOT NULL
    , UNIQUE KEY `nombre_usuario` (`nombre_usuario`)
    , UNIQUE KEY `correo` (`correo`)
    , UNIQUE KEY `id_sesion` (`id_sesion`)
);