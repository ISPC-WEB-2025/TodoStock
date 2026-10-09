# Guía de Pruebas Locales con Thunder Client / Postman

Esta guía detalla los pasos para probar manualmente los endpoints de la API REST de **CodeLab_Stock** en un entorno local.

---

## 🚀 Requisitos Previos

1. Asegurarse de que el servidor Backend esté levantado:
   ```powershell
   cd Backend
   venv\Scripts\python manage.py runserver
   ```
2. Tener instalada la extensión **Thunder Client** en VS Code o la aplicación **Postman**.
3. Base URL: `http://127.0.0.1:8000`

---

## 📋 Colección de Peticiones

### 1. Iniciar Sesión (Obtener Token de Autenticación)
- **Método**: `POST`
- **URL**: `http://127.0.0.1:8000/api/usuarios/login/`
- **Headers**:
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "email": "admin@codelab.com",
    "password": "<ADMIN_PASSWORD de tu .env>"
  }
  ```
- **Respuesta esperada**: `200 OK`
  ```json
  {
    "nombre": "Administrador",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "email": "admin@codelab.com",
    "es_admin": true,
    "es_empleado": false
  }
  ```
> **Nota**: Copiar el valor del `token` para incluirlo en el Header `Authorization: Token <tu_token>` en todas las peticiones siguientes.

---

### 2. Listar Todos los Proveedores
- **Método**: `GET`
- **URL**: `http://127.0.0.1:8000/api/inventario/proveedores/`
- **Headers**:
  - `Authorization`: `Token <tu_token>`
- **Respuesta esperada**: `200 OK` con la lista de proveedores registrados en la base de datos.

---

### 3. Búsqueda y Filtro de Proveedores en Tiempo Real
- **Método**: `GET`
- **URL**: `http://127.0.0.1:8000/api/inventario/proveedores/?search=Motores`
- **Headers**:
  - `Authorization`: `Token <tu_token>`
- **Respuesta esperada**: `200 OK` retornando únicamente aquellos proveedores cuyo nombre, CUIT o email coincidan con el término buscado.

---

### 4. Registrar un Nuevo Proveedor
- **Método**: `POST`
- **URL**: `http://127.0.0.1:8000/api/inventario/proveedores/`
- **Headers**:
  - `Authorization`: `Token <tu_token>`
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "nombre": "Aberturas del Litoral",
    "cuit": "30-44556677-8",
    "telefono": "351-5551234",
    "email": "ventas@aberturaslitoral.com",
    "direccion": "Av. Colón 4500"
  }
  ```
- **Respuesta esperada**: `201 Created` con los datos del proveedor creado y su `id_prov` asignado.

---

### 5. Registrar Entrada de Stock con Proveedor y Remito
- **Método**: `POST`
- **URL**: `http://127.0.0.1:8000/api/inventario/movimientos/`
- **Headers**:
  - `Authorization`: `Token <tu_token>`
  - `Content-Type`: `application/json`
- **Body (JSON)**:
  ```json
  {
    "tipo": "Entrada",
    "cantidad": 10,
    "motivo": "Remito R-0001-00088921 - Recepción de perfiles",
    "id_art": 1,
    "id_suc": 1,
    "id_prov": 1
  }
  ```
- **Respuesta esperada**: `201 Created` retornando el movimiento registrado con trazabilidad completa:
  ```json
  {
    "id_mov": 1,
    "tipo": "Entrada",
    "fecha_hora": "2026-08-18T07:28:07.123456Z",
    "stock_previo": 150,
    "cantidad": 10,
    "motivo": "Remito R-0001-00088921 - Recepción de perfiles",
    "id_art": 1,
    "id_suc": 1,
    "id_prov": 1,
    "id_usuario": 1,
    "nombre_producto": "Perfil de aluminio 45mm",
    "nombre_sucursal": "Fábrica Principal",
    "nombre_proveedor": "Aluminios Cba SRL",
    "cuit_proveedor": "30-12345678-9"
  }
  ```
