USE todostock;

INSERT INTO CATEGORIA (nombre) VALUES 
('Perfiles de aluminio'),
('Cortinas de enrollar'),
('Portones enrollables'),
('Accesorios'),
('Motores');

INSERT INTO PROVEEDOR (nombre, cuit, telefono, email, direccion) VALUES
('Aluminios Cba SRL', '30-12345678-9', '351-1234567', 'ventas@aluminioscba.com', 'Av. Fuerza Aérea 1234'),
('Motores Automatizados SA', '30-98765432-1', '351-7654321', 'contacto@motoresauto.com', 'Bv. Los Granaderos 555'),
('Portones & Aberturas del Centro SRL', '30-11223344-5', '351-4445566', 'ventas@portonescentro.com', 'Ruta 9 Km 12'),
('Herrajes & Accesorios Industriales SA', '30-33445566-7', '351-8889900', 'info@herrajesindustriales.com.ar', 'Av. Juan B. Justo 4100'),
('Distribuidora Metalúrgica del Norte', '30-55667788-9', '351-2223344', 'pedidos@metalurgicanorte.com', 'Av. La Voz del Interior 6200');

INSERT INTO SUCURSAL (nombre, direccion, es_central) VALUES
('Fábrica Principal',  'Calle Industrial 100', 1),
('Depósito Zona Sur',  'Av. Sabattini 3200',   0),
('Local Centro',       'Bv. San Juan 450',      0);

INSERT INTO PRODUCTO (nombre, descripcion, codigo, precio_venta, id_cat) VALUES
('Perfil de aluminio 45mm',      'Perfil para guías de cortinas',          'ALU-45',    12500.00, 1),
('Motor Tubular 50Nm',           'Motor para cortinas de enrollar pesadas', 'MOT-50',    85000.00, 5),
('Lama de aluminio inyectado',   'Lama para portones rodantes',             'LAM-PORT',   4500.50, 3),
('Perfil de aluminio 60mm',      'Perfil para guías de cortinas pesadas',   'ALU-60',    15800.00, 1),
('Perfil de aluminio 30mm',      'Perfil liviano para cortinas interiores', 'ALU-30',     9200.00, 1),
('Cortina de enrollar 2x2m',     'Cortina estándar para locales',           'COR-2X2',   45000.00, 2),
('Cortina de enrollar 3x2m',     'Cortina para aberturas grandes',          'COR-3X2',   68000.00, 2),
('Portón enrollable 4x2m',       'Portón para garaje residencial',          'PORT-4X2', 120000.00, 3),
('Portón enrollable 5x3m',       'Portón industrial reforzado',             'PORT-5X3', 195000.00, 3),
('Motor Tubular 30Nm',           'Motor para cortinas livianas',            'MOT-30',    62000.00, 5),
('Motor Tubular 100Nm',          'Motor industrial de alta potencia',       'MOT-100',  140000.00, 5),
('Control remoto 2 canales',     'Control para motores tubulares',          'CTRL-2C',    8500.00, 4),
('Soporte de techo aluminio',    'Soporte para instalación en techo',       'SOP-TECH',   3200.00, 4);

INSERT INTO PRODUCTO_PROVEEDOR (id_art, id_prov, precio_costo) VALUES
(1,  1,  9000.00),
(2,  2, 60000.00),
(3,  1,  3200.00),
(4,  1, 11000.00),
(5,  1,  6500.00),
(6,  3, 32000.00),
(7,  3, 48000.00),
(8,  3, 85000.00),
(9,  3,138000.00),
(10, 2, 44000.00),
(11, 2, 98000.00),
(12, 2,  5500.00),
(13, 1,  2100.00);

INSERT INTO STOCK_SUCURSAL (cantidad_stock, stock_min, id_art, id_suc) VALUES
(150, 50,  1, 1),
(20,   5,  2, 1),
(500, 100,  3, 2),
(80,  30,  4, 1),
(200, 60,  5, 1),
(15,   5,  6, 1),
(10,   3,  7, 2),
(8,    2,  8, 3),
(4,    1,  9, 3),
(25,  10, 10, 1),
(12,   4, 11, 2),
(50,  15, 12, 1),
(35,  10, 13, 1);