-- ============================================
--   TodoStock - Script de Base de Datos MySQL
-- ============================================

CREATE DATABASE IF NOT EXISTS todostock
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE todostock;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS MOVIMIENTO, STOCK_SUCURSAL, PRODUCTO_PROVEEDOR, PRODUCTO, SUCURSAL, PROVEEDOR, CATEGORIA;
SET FOREIGN_KEY_CHECKS = 1;
-- ============================================
--   CATEGORÍA
-- ============================================
CREATE TABLE CATEGORIA (
    id_cat  INT          NOT NULL AUTO_INCREMENT,
    nombre  VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_cat)
);

-- ============================================
--   PROVEEDOR
-- ============================================
CREATE TABLE PROVEEDOR (
    id_prov   INT          NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(200) NOT NULL,
    cuit      VARCHAR(20)  NOT NULL,
    telefono  VARCHAR(30)  NOT NULL,
    email     VARCHAR(150) NOT NULL,
    direccion VARCHAR(300) NOT NULL,
    PRIMARY KEY (id_prov),
    UNIQUE KEY uq_proveedor_cuit (cuit)
);

-- ============================================
--   SUCURSAL
-- ============================================
CREATE TABLE SUCURSAL (
    id_suc    INT          NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(100) NOT NULL,
    direccion VARCHAR(300) NOT NULL,
    es_central BOOLEAN     NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id_suc)
);

-- ============================================
--   PRODUCTO
-- ============================================
CREATE TABLE PRODUCTO (
    id_art      INT            NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(200)   NOT NULL,
    descripcion TEXT           NULL,
    codigo      VARCHAR(50)    NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_min_global INT       NOT NULL DEFAULT 0,
    id_cat      INT            NOT NULL,
    PRIMARY KEY (id_art),
    UNIQUE KEY uq_producto_codigo (codigo),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_cat) REFERENCES CATEGORIA (id_cat)
);

-- ============================================
--   PRODUCTO_PROVEEDOR
-- ============================================
CREATE TABLE PRODUCTO_PROVEEDOR (
    id_enlace   INT            NOT NULL AUTO_INCREMENT,
    id_art      INT            NOT NULL,
    id_prov     INT            NOT NULL,
    precio_costo DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_enlace),
    UNIQUE KEY uq_pp_art_prov (id_art, id_prov),
    CONSTRAINT fk_pp_producto
        FOREIGN KEY (id_art)  REFERENCES PRODUCTO  (id_art),
    CONSTRAINT fk_pp_proveedor
        FOREIGN KEY (id_prov) REFERENCES PROVEEDOR (id_prov)
);

-- ============================================
--   STOCK_SUCURSAL
-- ============================================
CREATE TABLE STOCK_SUCURSAL (
    id_stock       INT NOT NULL AUTO_INCREMENT,
    cantidad_stock INT NOT NULL DEFAULT 0,
    stock_min      INT NOT NULL DEFAULT 0,
    id_art         INT NOT NULL,
    id_suc         INT NOT NULL,
    PRIMARY KEY (id_stock),
    UNIQUE KEY uq_pp_art_suc (id_art, id_suc),
    CONSTRAINT fk_stock_producto
        FOREIGN KEY (id_art) REFERENCES PRODUCTO (id_art),
    CONSTRAINT fk_stock_sucursal
        FOREIGN KEY (id_suc) REFERENCES SUCURSAL (id_suc)
);

-- ============================================
--   MOVIMIENTO
-- ============================================
CREATE TABLE MOVIMIENTO (
    id_mov     INT          NOT NULL AUTO_INCREMENT,
    tipo       ENUM('Entrada','Salida','Traslado') NOT NULL,
    fecha_hora DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stock_previo INT NULL,
    cantidad   INT          NOT NULL,
    motivo     VARCHAR(255) NULL,
    id_art     INT          NOT NULL,
    id_suc     INT          NOT NULL,
    id_prov    INT          NULL,
    id_usuario BIGINT       NULL,
    PRIMARY KEY (id_mov),
    CONSTRAINT fk_mov_producto
        FOREIGN KEY (id_art) REFERENCES PRODUCTO (id_art),
    CONSTRAINT fk_mov_sucursal
        FOREIGN KEY (id_suc) REFERENCES SUCURSAL (id_suc),
    CONSTRAINT fk_mov_proveedor
        FOREIGN KEY (id_prov) REFERENCES PROVEEDOR (id_prov),
    CONSTRAINT fk_mov_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios_usuario (id)
);

-- ============================================
--   DATOS DE PRUEBA
-- ===========================================

INSERT INTO CATEGORIA (nombre) VALUES 
('Perfiles de aluminio'),
('Cortinas de enrollar'),
('Portones enrollables'),
('Accesorios');

INSERT INTO PROVEEDOR (nombre, cuit, telefono, email, direccion) VALUES
('Aluminios Cba SRL', '30-12345678-9', '351-1234567', 'ventas@aluminioscba.com', 'Av. Fuerza Aérea 1234'),
('Motores Automatizados SA', '30-98765432-1', '351-7654321', 'contacto@motoresauto.com', 'Bv. Los Granaderos 555'),
('Portones & Aberturas del Centro SRL', '30-11223344-5', '351-4445566', 'ventas@portonescentro.com', 'Ruta 9 Km 12'),
('Herrajes & Accesorios Industriales SA', '30-33445566-7', '351-8889900', 'info@herrajesindustriales.com.ar', 'Av. Juan B. Justo 4100'),
('Distribuidora Metalúrgica del Norte', '30-55667788-9', '351-2223344', 'pedidos@metalurgicanorte.com', 'Av. La Voz del Interior 6200');

INSERT INTO SUCURSAL (nombre, direccion) VALUES
('Fábrica Principal', 'Calle Industrial 100'),
('Depósito Zona Sur', 'Av. Sabattini 3200');

INSERT INTO PRODUCTO (nombre, descripcion, codigo, precio_venta, id_cat) VALUES
('Perfil de aluminio 45mm', 'Perfil para guías de cortinas', 'ALU-45', 12500.00, 1),
('Motor Tubular 50Nm', 'Motor para cortinas de enrollar pesadas', 'MOT-50', 85000.00, 4),
('Lama de aluminio inyectado', 'Lama para portones rodantes', 'LAM-PORT', 4500.50, 3);

INSERT INTO PRODUCTO_PROVEEDOR (id_art, id_prov, precio_costo) VALUES
(1, 1, 9000.00),  -- El Perfil se lo compramos a Aluminios Cba
(2, 2, 60000.00), -- El Motor se lo compramos a Motores Automatizados
(3, 1, 3200.00);  -- La Lama se la compramos a Aluminios Cba

INSERT INTO STOCK_SUCURSAL (cantidad_stock, stock_min, id_art, id_suc) VALUES
(150, 50, 1, 1), -- 150 perfiles en Fábrica Principal
(20, 5, 2, 1),   -- 20 motores en Fábrica Principal
(500, 100, 3, 2); -- 500 lamas en Depósito Zona Sur