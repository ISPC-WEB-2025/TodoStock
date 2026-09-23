# Guía de Integración REST API para Aplicaciones Móviles (CodeLab Stock)

Documentación técnica y catálogo de endpoints preparados para el consumo desde aplicaciones móviles (**Android**, **Flutter**, **React Native**, **iOS**).

---

## 1. Conectividad y URLs Base

| Entorno / Dispositivo | URL Base | Observaciones |
| :--- | :--- | :--- |
| **Producción Remoto (Nube)** | `https://<tu_usuario>.alwaysdata.net/` | Conexión segura HTTPS pública desde datos móviles o cualquier red exterior. |
| **Emulador Android Oficial** | `http://10.0.2.2:8000/` | `10.0.2.2` apunta al `localhost` del host de desarrollo local. |
| **Simulador iOS** | `http://127.0.0.1:8000/` | Accede de forma directa al puerto local de desarrollo. |
| **Dispositivo Físico (Wi-Fi Local)** | `http://<IP_LOCAL_PC>:8000/` | Ej. `http://192.168.1.50:8000/` (misma red Wi-Fi de desarrollo). |

> **Nota de Despliegue**: Para la puesta en marcha de la API en la nube con base de datos MySQL, consultar la [Guía de Despliegue en Alwaysdata](DEPLOY_ALWAYSDATA.md). El backend cuenta con `ALLOWED_HOSTS` configurable y `CORS_ALLOW_ALL_ORIGINS = True` para admitir conexiones desde aplicaciones móviles sin bloqueos de red.

---

## 2. Autenticación y Manejo de Tokens JWT

El sistema utiliza **JSON Web Tokens (JWT)** mediante `djangorestframework-simplejwt`.

- **Access Token**: Vigencia de **60 minutos** (se envía en cada petición protegida).
- **Refresh Token**: Vigencia de **5 días** (permite obtener un nuevo access token silenciosamente).

### 2.1 Cabecera de Autorización Obligatoria
En todos los endpoints protegidos, se debe incluir la cabecera HTTP:
```http
Authorization: Bearer <access_token>
```

---

## 3. Formato Estándar de Errores

En caso de error (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`), el backend responde con una estructura JSON homogénea:

```json
{
  "error": "Stock insuficiente.",
  "status_code": 400,
  "stock_disponible": 5,
  "cantidad_solicitada": 10
}
```

O en caso de validación de formulario/campos:
```json
{
  "error": "Datos inválidos.",
  "status_code": 400,
  "detalle": {
    "codigo": ["Ya existe un producto con el código 'ALU-45'."],
    "stock_min_global": ["El stock mínimo global no puede ser negativo."]
  }
}
```

---

## 4. Catálogo de Endpoints para la App Móvil

### 4.1 Autenticación y Perfil

#### `POST /api/usuarios/login/`
Inicia sesión y retorna los tokens JWT y datos de perfil.
- **Body**:
  ```json
  {
    "email": "vendedor@test.com",
    "password": "mi_password_seguro"
  }
  ```
- **Respuesta 200 OK**:
  ```json
  {
    "nombre": "Juan Pérez",
    "email": "vendedor@test.com",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "es_admin": false,
    "es_empleado": true
  }
  ```

#### `POST /api/usuarios/token/refresh/`
Renueva un access token expirado utilizando el refresh token.
- **Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
  }
  ```
- **Respuesta 200 OK**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
  }
  ```

#### `GET /api/usuarios/me/`
Obtiene el perfil y roles del usuario actualmente autenticado (ideal al iniciar la app con token guardado).
- **Cabecera**: `Authorization: Bearer <access>`
- **Respuesta 200 OK**:
  ```json
  {
    "id": 2,
    "email": "vendedor@test.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "35123456",
    "es_admin": false,
    "es_empleado": true,
    "activo": true
  }
  ```

---

### 4.2 Catálogo de Productos y Escaneo de Código de Barras

#### `GET /api/inventario/productos/?codigo={CODIGO}` (Escáner de Barras / QR)
Búsqueda exacta para lectores de código de barras o cámara del dispositivo móvil.
- **Ejemplo**: `GET /api/inventario/productos/?codigo=ALU-45`
- **Respuesta 200 OK**:
  ```json
  [
    {
      "id_art": 1,
      "nombre": "Perfil de aluminio 45mm",
      "descripcion": "Perfil para guías de cortinas",
      "codigo": "ALU-45",
      "precio_venta": "12500.00",
      "stock_min_global": 50,
      "stock_total": 150,
      "id_cat": 1,
      "categoria": {
        "id_cat": 1,
        "nombre": "Perfiles de aluminio",
        "total_articulos": 3
      }
    }
  ]
  ```

#### `GET /api/inventario/productos/?search={texto}&id_cat={id}&ordering={campo}`
Búsqueda y filtrado dinámico de artículos.
- **Query Params**:
  - `search`: busca por coincidencia en `nombre` o `codigo`.
  - `id_cat`: filtra por ID de categoría.
  - `ordering`: ordena por `nombre`, `-nombre`, `precio_venta`, `-precio_venta`, `id_art`.
- **Respuesta 200 OK**: Array de objetos `Producto`.

#### `GET /api/inventario/productos/{id}/stock/` (Stock Multi-Sede de un Producto)
Retorna la disponibilidad física de un producto en todas las sucursales de la red.
- **Ejemplo**: `GET /api/inventario/productos/1/stock/`
- **Respuesta 200 OK**:
  ```json
  [
    {
      "id_stock": 1,
      "id_art": 1,
      "id_suc": 1,
      "nombre_producto": "Perfil de aluminio 45mm",
      "nombre_sucursal": "Fábrica Principal",
      "cantidad_stock": 150,
      "stock_min": 50
    },
    {
      "id_stock": 4,
      "id_art": 1,
      "id_suc": 2,
      "nombre_producto": "Perfil de aluminio 45mm",
      "nombre_sucursal": "Depósito Zona Sur",
      "cantidad_stock": 0,
      "stock_min": 50
    }
  ]
  ```

---

### 4.3 Sucursales y Categorías

#### `GET /api/inventario/sucursales/`
Listado de todas las sucursales con métricas de stock.
- **Respuesta 200 OK**:
  ```json
  [
    {
      "id_suc": 1,
      "nombre": "Fábrica Principal",
      "direccion": "Calle Industrial 100",
      "total_articulos": 13,
      "articulos_con_stock": 11,
      "articulos_sin_stock": 2,
      "articulos_alerta": 1
    }
  ]
  ```

#### `GET /api/inventario/sucursales/{id}/inventario/?solo_con_stock=true`
Inventario completo de una sede (con opción para omitir artículos en 0).
- **Query Params**:
  - `solo_con_stock=true`: Oculta artículos sin existencias físicas en esa sucursal.
  - `search=texto`: Filtra por nombre o código dentro de la sucursal.

#### `GET /api/inventario/categorias/`
Listado de categorías del inventario.
- **Respuesta 200 OK**:
  ```json
  [
    {
      "id_cat": 1,
      "nombre": "Perfiles de aluminio",
      "total_articulos": 3
    }
  ]
  ```

---

### 4.4 Operaciones de Movimiento de Stock desde el Móvil

#### `POST /api/inventario/movimientos/` — Registrar Salida / Venta en Salón
Descuenta stock inmediatamente con validación atómica (`select_for_update`) y previene saldo negativo.
- **Cabecera**: `Authorization: Bearer <access>`
- **Body**:
  ```json
  {
    "tipo": "Salida",
    "cantidad": 2,
    "id_art": 1,
    "id_suc": 1,
    "motivo": "Venta en mostrador - Ticket #4920"
  }
  ```
- **Respuesta 201 Created**:
  ```json
  {
    "id_mov": 58,
    "tipo": "Salida",
    "cantidad": 2,
    "stock_previo": 150,
    "fecha_hora": "2026-08-18T12:00:00Z",
    "motivo": "Venta en mostrador - Ticket #4920",
    "id_art": 1,
    "id_suc": 1,
    "nombre_producto": "Perfil de aluminio 45mm",
    "nombre_sucursal": "Fábrica Principal"
  }
  ```

#### `POST /api/inventario/movimientos/` — Registrar Traslado entre Sedes
Mueve stock atómicamente desde la sucursal de origen (`id_suc`) hacia la de destino (`id_suc_destino`).
- **Cabecera**: `Authorization: Bearer <access>`
- **Body**:
  ```json
  {
    "tipo": "Traslado",
    "cantidad": 10,
    "id_art": 1,
    "id_suc": 1,
    "id_suc_destino": 2,
    "motivo": "Reabastecimiento Depósito Sur"
  }
  ```
- **Respuesta 201 Created**.

#### `GET /api/inventario/movimientos/?id_suc={id}&id_art={id}&tipo={tipo}`
Consulta del historial y trazabilidad de movimientos.
- **Query Params**:
  - `id_suc`: filtra por sucursal.
  - `id_art`: filtra por producto.
  - `tipo`: `Entrada`, `Salida`, `Traslado`.
  - `ordering=-fecha_hora`: orden descendente por fecha.

---

## 5. Ejemplos de Implementación en Código Móvil

### Flutter / Dart (Dio HTTP Client)
```dart
import 'package:dio/dio.dart';

class ApiService {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: 'http://10.0.2.2:8000/api/',
    connectTimeout: const Duration(seconds: 10),
  ));

  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  // Buscar producto por código de barras escaneado
  Future<Map<String, dynamic>?> buscarPorCodigo(String barcode) async {
    final response = await _dio.get('inventario/productos/', queryParameters: {'codigo': barcode});
    final List data = response.data;
    return data.isNotEmpty ? data.first : null;
  }

  // Registrar salida de stock
  Future<bool> registrarSalida({
    required int idArt,
    required int idSuc,
    required int cantidad,
    String? motivo,
  }) async {
    final response = await _dio.post('inventario/movimientos/', data: {
      'tipo': 'Salida',
      'id_art': idArt,
      'id_suc': idSuc,
      'cantidad': cantidad,
      'motivo': motivo ?? 'Salida registrada desde App Móvil',
    });
    return response.statusCode == 201;
  }
}
```

### Kotlin / Android (Retrofit)
```kotlin
interface StockApiService {
    @POST("usuarios/login/")
    suspend fun login(@Body credenciales: LoginRequest): Response<LoginResponse>

    @GET("usuarios/me/")
    suspend fun getPerfil(@Header("Authorization") token: String): Response<UsuarioDto>

    @GET("inventario/productos/")
    suspend fun buscarPorCodigo(
        @Header("Authorization") token: String,
        @Query("codigo") codigo: String
    ): Response<List<ProductoDto>>

    @GET("inventario/productos/{id}/stock/")
    suspend fun getStockPorSedes(
        @Header("Authorization") token: String,
        @Path("id") idArt: Int
    ): Response<List<StockSucursalDto>>

    @POST("inventario/movimientos/")
    suspend fun registrarMovimiento(
        @Header("Authorization") token: String,
        @Body payload: MovimientoRequest
    ): Response<MovimientoDto>
}
```
