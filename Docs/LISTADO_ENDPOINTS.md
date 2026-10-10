# 📋 Listado Completo de Endpoints — Backend TodoStock

Documento de referencia para el equipo de desarrollo (Frontend, Mobile y Backend). Describe de forma sencilla para qué sirve cada endpoint, qué método HTTP utiliza, quién tiene acceso y qué datos espera o devuelve.

---

## 📌 Convenciones y Base URLs

- **Base URL local (Web / Postman):** `http://localhost:8000/`
- **Base URL Emulador Android:** `http://10.0.2.2:8000/`
- **Base URL Dispositivo Físico:** `http://<TU_IP_LOCAL>:8000/` (ej. `http://192.168.1.50:8000/`)
- **Autenticación:** Los endpoints que requieren autenticación necesitan el encabezado:
  ```http
  Authorization: Bearer <access_token>
  ```

---

## 🔐 1. Módulo de Autenticación y Cuentas de Usuario (`/api/usuarios/`)

### 1.1 Acceso y Registro Público

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/usuarios/login/` | Público | **Iniciar sesión.** Envía email y contraseña. Retorna los tokens JWT (`access` y `refresh`), datos del usuario y sus roles (`es_admin`, `es_empleado`). Si la cuenta no fue aprobada aún, avisa con un código 403. |
| `POST` | `/api/usuarios/token/refresh/` | Público | **Renovar sesión.** Envía el token `refresh` y devuelve un nuevo `access_token` cuando el anterior vence, sin pedirle al usuario que vuelva a escribir su contraseña. |
| `POST` | `/api/usuarios/registro/` | Público | **Registrar nuevo usuario.** Envía nombre, email, DNI, fecha de nacimiento y contraseña. La cuenta se crea inactiva a la espera de que un Administrador la apruebe. |
| `POST` | `/api/usuarios/contacto/` | Público | **Formulario de contacto y soporte.** Envía asunto, mensaje y email. Guarda la consulta en los logs del servidor para asistencia técnica. |

---

### 1.2 Perfil Propio del Usuario Autenticado (`/me/`)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/usuarios/me/` | Autenticado | **Ver mi perfil.** Devuelve los datos del usuario conectado (nombre, email, DNI, rol asignado, estado). Ideal para cargar la info al abrir la app o refrescar pantalla. |
| `PATCH` | `/api/usuarios/me/` | Autenticado | **Editar mis datos.** Permite al usuario actualizar su propio nombre, DNI o fecha de nacimiento. No permite cambiarse el rol ni el email por seguridad. |
| `DELETE` | `/api/usuarios/me/` | Autenticado | **Darse de baja.** Desactiva la cuenta propia (`is_active = False`) y asienta automáticamente el registro de baja en la tabla de auditoría con fecha y correo del usuario (TK51/TK59). No elimina el registro de la base de datos (un admin puede reactivarla si fue un error). |
| `POST` | `/api/usuarios/me/change-password/` | Autenticado | **Cambiar mi contraseña.** Envía la contraseña actual y la nueva (mínimo 9 caracteres con letras, números y símbolos). |

---

### 1.4 Auditoría de Seguridad y Trazabilidad (Exclusivo Administradores)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/usuarios/auditoria/` | Admin | **Consultar logs de auditoría.** Devuelve el listado histórico de eventos de seguridad (bajas voluntarias/administrativas, altas, inicios de sesión exitosos y fallidos, cambios de rol y claves). Ordenado por fecha descendente. |
| `GET` | `/api/usuarios/auditoria/<id>/` | Admin | **Detalle de un evento de auditoría.** Información completa de un registro de auditoría individual (fecha, evento, correo, IP de origen y descripción). |

---


### 1.3 Administración de Usuarios y Roles (Exclusivo Administradores)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/usuarios/roles/` | Autenticado | **Listar roles del sistema.** Devuelve los roles existentes (`ADMINISTRADOR`, `EMPLEADO`). Muy útil para llenar desplegables/combos en formularios. |
| `GET` | `/api/usuarios/` | Admin | **Listar todos los usuarios.** Devuelve el listado completo de usuarios registrados con su estado y rol. |
| `POST` | `/api/usuarios/` | Admin | **Crear un usuario nuevo directamente.** Permite al administrador crear un usuario ya activo y con rol asignado. |
| `GET` | `/api/usuarios/<id>/` | Admin | **Ver detalle de un usuario.** Información completa de un usuario específico según su ID. |
| `PUT` / `PATCH` | `/api/usuarios/<id>/` | Admin | **Editar usuario / Aprobar cuenta.** Permite cambiar datos de un usuario o **aprobarlo** enviando `{"is_active": true, "rol_id": 2}`. |
| `DELETE` | `/api/usuarios/<id>/` | Admin | **Desactivar usuario.** Baja lógica de una cuenta (`is_active = False`). |
| `POST` | `/api/usuarios/<id>/reset-password/` | Admin | **Restablecer contraseña de un usuario.** Permite a un administrador asignarle una nueva clave a un empleado que la haya olvidado. |

---

## 📦 2. Módulo de Inventario y Catálogo (`/api/inventario/`)

### 2.1 Productos

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/productos/` | Autenticado | **Catálogo de productos.** Devuelve los productos. Permite buscar por texto (`?search=tornillo`), filtrar por código de barras/SKU (`?codigo=ALU-45`) o por categoría (`?id_cat=1`). |
| `POST` | `/api/inventario/productos/` | Admin | **Crear producto.** Da de alta un nuevo producto con su nombre, código, precio de venta, categoría y stock mínimo global. |
| `GET` | `/api/inventario/productos/<id>/` | Autenticado | **Detalle de un producto.** Información individual completa de un producto. |
| `PUT` / `PATCH` | `/api/inventario/productos/<id>/` | Admin | **Editar producto.** Modifica precio, descripción, nombre o categoría de un producto. |
| `DELETE` | `/api/inventario/productos/<id>/` | Admin | **Eliminar producto.** Borra el producto del catálogo. Si tiene stock activo o historial de movimientos, no permite borrarlo y devuelve un mensaje explicativo (error 400). |
| `GET` | `/api/inventario/productos/<id>/stock/` | Autenticado | **Ver stock del producto en todas las sedes.** Muestra cuánto stock físico hay de ese producto en cada sucursal. |

---

### 2.2 Categorías de Productos

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/categorias/` | Autenticado | **Listar categorías.** Muestra todas las categorías creadas (ej. Tornillería, Perfiles, Herramientas). Permite buscar por nombre con `?search=`. |
| `POST` | `/api/inventario/categorias/` | Admin | **Crear categoría.** Crea una nueva categoría. |
| `GET` | `/api/inventario/categorias/<id>/` | Autenticado | **Detalle de categoría.** Información de una categoría por su ID. |
| `PUT` / `PATCH` | `/api/inventario/categorias/<id>/` | Admin | **Editar categoría.** Modifica el nombre o descripción de la categoría. |
| `DELETE` | `/api/inventario/categorias/<id>/` | Admin | **Eliminar categoría.** Borra una categoría (valida que no tenga productos asociados). |
| `GET` | `/api/inventario/categorias/<id>/productos/` | Autenticado | **Productos de una categoría.** Devuelve todos los artículos que pertenecen a esa categoría específica. |

---

### 2.3 Sucursales

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/sucursales/` | Autenticado | **Listar sucursales.** Muestra las sedes físicas del negocio (nombre, dirección, si es Casa Central). |
| `POST` | `/api/inventario/sucursales/` | Admin | **Crear sucursal.** Agrega una nueva sucursal al sistema. |
| `GET` | `/api/inventario/sucursales/<id>/` | Autenticado | **Detalle de sucursal.** Datos de una sede puntual. |
| `PUT` / `PATCH` | `/api/inventario/sucursales/<id>/` | Admin | **Editar sucursal.** Modifica nombre, dirección o estado de la sucursal. |
| `DELETE` | `/api/inventario/sucursales/<id>/` | Admin | **Eliminar sucursal.** Borra la sede (valida que no sea Casa Central, que no tenga stock activo ni historial de movimientos). |
| `GET` | `/api/inventario/sucursales/<id>/inventario/` | Autenticado | **Inventario completo de la sucursal.** Lista los productos en esa sucursal, la cantidad actual y el stock mínimo (para alertas de bajo stock). Permite filtrar con `?solo_con_stock=true` y `?search=`. |

---

### 2.4 Proveedores

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/proveedores/` | Admin | **Listar proveedores.** Muestra las empresas o personas que proveen mercadería (nombre, CUIT, email, teléfono, dirección). |
| `POST` | `/api/inventario/proveedores/` | Admin | **Crear proveedor.** Da de alta un nuevo proveedor. |
| `GET` | `/api/inventario/proveedores/<id>/` | Admin | **Detalle de proveedor.** Información puntual de un proveedor. |
| `PUT` / `PATCH` | `/api/inventario/proveedores/<id>/` | Admin | **Editar proveedor.** Actualiza información de contacto o fiscal de un proveedor. |
| `DELETE` | `/api/inventario/proveedores/<id>/` | Admin | **Eliminar proveedor.** Borra un proveedor. |

---

### 2.5 Asociación Producto - Proveedor

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/producto-proveedor/` | Admin | **Listar relaciones producto-proveedor.** Consulta qué proveedores abastecen qué artículos. |
| `POST` | `/api/inventario/producto-proveedor/` | Admin | **Vincular producto con proveedor.** Asocia un artículo con un proveedor. |
| `GET` | `/api/inventario/producto-proveedor/<id>/` | Admin | **Ver relación puntual.** Consulta el detalle de un vínculo. |
| `PUT` / `PATCH` | `/api/inventario/producto-proveedor/<id>/` | Admin | **Modificar relación.** Actualiza los datos del vínculo. |
| `DELETE` | `/api/inventario/producto-proveedor/<id>/` | Admin | **Eliminar relación.** Desvincula el producto del proveedor. |

---

### 2.6 Control Físico de Stock (`/stock/`)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/stock/` | Autenticado | **Tabla general de existencias.** Consulta el stock por producto y por sucursal. Admite filtros como `?id_art=1` o `?id_suc=2`. |
| `POST` | `/api/inventario/stock/` | Admin | **Inicializar stock.** Asigna existencias iniciales o stock mínimo a un producto en una sucursal específica. |
| `GET` | `/api/inventario/stock/<id>/` | Autenticado | **Ver registro de stock.** Detalle de una fila puntual de existencias. |
| `PUT` / `PATCH` | `/api/inventario/stock/<id>/` | Admin | **Ajustar stock directamente.** Modifica manualmente la cantidad o el stock mínimo de ese registro. |
| `DELETE` | `/api/inventario/stock/<id>/` | Admin | **Eliminar registro de stock.** Borra el registro de existencias físicas. |

---

### 2.7 Movimientos de Mercadería (`/movimientos/`)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventario/movimientos/` | Autenticado | **Historial y auditoría de movimientos.** Consulta todos los movimientos ocurridos. Permite filtrar por tipo (`?tipo=Salida`), por sucursal (`?id_suc=1`) o por producto (`?id_art=1`). |
| `POST` | `/api/inventario/movimientos/` | Autenticado / Admin | **Registrar un movimiento físico de stock.** Impacta directamente en las cantidades de stock de forma atómica y segura. |

#### Tipos de Movimientos posibles en el `POST`:
1. **`"Entrada"`** *(Solo Admin)*: Ingreso de mercadería comprada a un proveedor hacia la Casa Central. Incrementa el stock disponible.
   - Datos: `tipo`, `cantidad`, `id_art`, `id_suc`, `id_prov`, `motivo` (ej. remito o factura).
2. **`"Salida"`** *(Admin y Empleados)*: Descuenta mercadería por venta mostrador, merma o rotura. Valida automáticamente que haya suficiente stock disponible antes de restar.
   - Datos: `tipo`, `cantidad`, `id_art`, `id_suc`, `motivo` (ej. "Venta Ticket #104").
3. **`"Traslado"`** *(Admin y Empleados)*: Mueve mercadería de una sucursal a otra. Descuenta del origen y suma en el destino en un solo paso protegido.
   - Datos: `tipo`, `cantidad`, `id_art`, `id_suc` (origen), `id_suc_destino` (destino), `motivo`.

---

## 🛍️ 3. Módulo de Vendedor (`/api/vendedor/`)

| Método | Endpoint | Acceso | ¿Para qué sirve? |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/vendedor/` | Autenticado | **Índice del módulo vendedor.** Devuelve el enlace hacia el catálogo de venta. |
| `GET` | `/api/vendedor/productos/` | Autenticado | **Catálogo simplificado para venta.** Devuelve la lista de productos optimizada con precios e identificación para consultas rápidas de ventas en mostrador. |

---

## 💡 Resumen Rápido para Compartir

- **Para iniciar sesión o ver usuarios:** Todo cuelga de `/api/usuarios/` (`login/`, `registro/`, `me/`, `roles/`).
- **Para ver productos y categorías:** Cuelga de `/api/inventario/productos/` y `/api/inventario/categorias/`.
- **Para consultar stock de una tienda:** Usar `/api/inventario/sucursales/<id>/inventario/` (avisa si está bajo de stock).
- **Para vender, trasladar o ingresar stock:** Usar `POST /api/inventario/movimientos/` indicando `Salida`, `Traslado` o `Entrada`.
- **Para buscar un producto por código de barras / QR:** Usar `/api/inventario/productos/?codigo=<codigo>`.
