# Guía de Integración REST API para App Mobile — TodoStock

Documentación técnica del catálogo de endpoints actualizado para el consumo desde la aplicación móvil Android (Java 17 / Android Studio Giraffe). Última actualización: octubre 2026.

---

## 1. Conectividad y URLs Base

| Entorno | URL Base | Observaciones |
| :--- | :--- | :--- |
| **Producción (Nube)** | `https://<usuario>.alwaysdata.net/` | HTTPS pública desde datos móviles o cualquier red. |
| **Emulador Android** | `http://10.0.2.2:8000/` | `10.0.2.2` apunta al `localhost` del host de desarrollo. |
| **Dispositivo Físico (Wi-Fi local)** | `http://<IP_LOCAL_PC>:8000/` | Misma red Wi-Fi. Ej: `http://192.168.1.50:8000/`. |

> **CORS y ALLOWED_HOSTS:** El backend tiene `CORS_ALLOW_ALL_ORIGINS = True` y `ALLOWED_HOSTS = ['*']` en desarrollo para admitir peticiones desde emuladores y dispositivos físicos sin bloqueos.

---

## 2. Autenticación JWT

- **Access Token:** Vigencia **60 minutos**.
- **Refresh Token:** Vigencia **5 días**.
- **Header obligatorio en endpoints protegidos:**
  ```
  Authorization: Bearer <access_token>
  ```
- **Renovación silenciosa:** `POST /api/usuarios/token/refresh/` con `{"refresh": "<token>"}`.

---

## 3. Formato Estándar de Errores

```json
{ "error": "Descripción del error." }
```

Para errores de validación de campos (HTTP 400):
```json
{ "error": "Datos inválidos", "detalle": { "campo": ["mensaje"] } }
```

---

## 4. Catálogo de Endpoints

### 4.1 Autenticación y Perfil de Usuario

#### `POST /api/usuarios/login/`
Inicia sesión y retorna tokens JWT y datos del perfil para poblar el menú principal (US01).

- **Body:** `{ "email": "...", "password": "..." }`
- **Respuesta 200 OK:**
  ```json
  {
    "id": 2,
    "nombre": "Juan Pérez",
    "email": "jperez@empresa.com",
    "access": "eyJ...",
    "refresh": "eyJ...",
    "token": "eyJ...",
    "es_admin": false,
    "es_empleado": true
  }
  ```
- **Respuesta 403 si cuenta inactiva (pendiente de aprobación):**
  ```json
  { "error": "Cuenta pendiente de aprobación por el administrador." }
  ```

#### `POST /api/usuarios/token/refresh/`
Renueva un access token expirado.
- **Body:** `{ "refresh": "eyJ..." }`
- **Respuesta 200:** `{ "access": "eyJ..." }`

#### `GET /api/usuarios/me/`
Perfil completo del usuario autenticado. Usarlo al iniciar la app con token guardado (US12).
- **Respuesta 200:**
  ```json
  {
    "id": 2,
    "email": "jperez@empresa.com",
    "nombre": "Juan Pérez",
    "dni": "35123456",
    "fecha_nacimiento": "1990-05-20",
    "rol": { "id": 2, "nombre": "EMPLEADO", "descripcion": "..." },
    "is_active": true,
    "is_superuser": false,
    "es_admin": false,
    "es_empleado": true
  }
  ```

#### `PATCH /api/usuarios/me/`
Actualiza los datos personales propios. Campos sensibles (`rol`, `email`, `is_active`, `is_superuser`) son ignorados aunque lleguen en el body (US12, ADR-0008).
- **Body (todos opcionales):** `{ "nombre": "Nuevo nombre", "dni": "35000001", "fecha_nacimiento": "1990-05-20" }`
- **Respuesta 200:** perfil actualizado.

#### `DELETE /api/usuarios/me/`
Desactiva la cuenta propia (`is_active = False`). No borra el registro. El admin puede reactivarla (US11).
- **Respuesta 200:** `{ "mensaje": "Cuenta desactivada. El administrador puede reactivarla cuando lo solicites." }`

#### `POST /api/usuarios/me/change-password/`
Permite al usuario autenticado cambiar su propia contraseña (US12 / ADR-0008).
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:**
  ```json
  {
    "password_actual": "MiPasswordVieja1!",
    "nueva_password": "MiPasswordNueva2026!"
  }
  ```
- **Regla de Contraseñas (OWASP / Mobile README):** Mínimo 9 caracteres, incluyendo letras, números y al menos un carácter especial estándar imprimible (`string.punctuation`). No se permiten espacios en blanco.
- **Respuesta 200:** `{ "mensaje": "Contraseña actualizada exitosamente." }`
- **Respuesta 400:** Si la clave actual no coincide, si es idéntica a la anterior o si no cumple con la regla de 9 caracteres.

#### `POST /api/usuarios/registro/`
Registro de usuario nuevo. La cuenta queda inactiva hasta que un admin la apruebe (US07).
- **Body:** `{ "nombre": "...", "email": "...", "dni": "12345678", "fdn": "1995-03-15", "password": "..." }`
- **Respuesta 201:** `{ "mensaje": "Cuenta creada. Aguardá la aprobación del administrador para poder ingresar." }`

#### `POST /api/usuarios/contacto/`
Envía una consulta de soporte. Se registra en el log del servidor. No requiere autenticación (US04).
- **Body:** `{ "asunto": "Problema con el inventario", "mensaje": "No puedo ver el stock...", "email": "opcional@email.com" }`
- **Respuesta 200:** `{ "mensaje": "Consulta recibida. Nos pondremos en contacto a la brevedad." }`

---

### 4.2 Gestión de Usuarios (Admin)

#### Jerarquía y Blindaje Administrativo (ADR-0008):
- **Super Administrador (`is_superuser=True`):** Puede crear, editar, asignar rol `ADMINISTRADOR`, resetear credenciales y desactivar cualquier cuenta. Su propia cuenta raíz está blindada contra desactivación.
- **Administrador Estándar (`es_admin=True`):** Solo puede gestionar cuentas operativas (`EMPLEADO` / `VENTAS` / `DEPOSITO`). Si intenta modificar, desactivar o resetear a otro Administrador o al Super Administrador, la API retorna `403 Forbidden` (`{"detail": "Acción reservada al Super Administrador."}`). Tampoco puede promover usuarios a `ADMINISTRADOR`.
- **Desacople de contraseñas:** El endpoint `PUT/PATCH /api/usuarios/<id>/` ignora el campo `password`. La gestión de contraseñas de terceros se canaliza exclusivamente por `/reset-password/`.

#### `GET /api/usuarios/`
Lista todos los usuarios. Requiere auth. Solo admins pueden modificar.
- Cada usuario incluye: `id`, `email`, `nombre`, `dni`, `fecha_nacimiento`, `rol`, `is_active`, `is_superuser`.

#### `PUT /api/usuarios/<id>/`
Edita un usuario. Solo admins. Para aprobar una cuenta, enviar `{ "is_active": true, "rol_id": 2 }`.

#### `DELETE /api/usuarios/<id>/`
Baja lógica: `is_active = False`. Solo admins. No borra el registro.

#### `POST /api/usuarios/<id>/reset-password/`
Reseteo administrativo de contraseñas (US08 / ADR-0008).
- **Headers:** `Authorization: Bearer <access_token>` (Admin o Superuser)
- **Body:** `{ "nueva_password": "NuevaPasswordRobusta1!" }`
- **Respuesta 200:** `{ "mensaje": "Contraseña del usuario '<email>' restablecida exitosamente." }`
- **Respuesta 403:** Si un admin regular intenta resetear a otro admin o al superuser.

#### `GET /api/usuarios/roles/`
Lista los roles disponibles para poblar selectores en la app (US08). Solo lectura, requiere auth.
- **Respuesta 200:**
  ```json
  [
    { "id": 1, "nombre": "ADMINISTRADOR", "descripcion": "Rol con control total del sistema" },
    { "id": 2, "nombre": "EMPLEADO", "descripcion": "Rol operativo" }
  ]
  ```

---

### 4.3 Inventario y Productos

#### `GET /api/inventario/sucursales/`
Lista todas las sucursales activas con métricas de stock. Útil para la pantalla de selección de sucursal activa (US02).

#### `GET /api/inventario/sucursales/<id>/inventario/?solo_con_stock=true&search=texto`
Inventario de una sucursal con alertas de umbral (US03).
- **Respuesta 200 (cada ítem):**
  ```json
  {
    "id_stock": 1,
    "id_art": 1,
    "id_suc": 1,
    "nombre_producto": "Perfil de aluminio 45mm",
    "nombre_sucursal": "Fábrica Principal",
    "codigo_producto": "ALU-45",
    "precio_venta": "12500.00",
    "cantidad_stock": 150,
    "stock_min": 50
  }
  ```
  > Para detectar alerta de umbral bajo: `cantidad_stock <= stock_min`.

#### `GET /api/inventario/productos/?codigo=<SKU>` — Escaneo de Código de Barras
Búsqueda exacta por código. Optimizada para respuesta instantánea desde escáner o cámara.

#### `GET /api/inventario/productos/?search=texto&id_cat=1&ordering=nombre`
Búsqueda y filtrado de catálogo de productos.

#### `POST /api/inventario/productos/`
Alta de producto nuevo. Solo admins (US05).
- **Body:** `{ "nombre": "...", "codigo": "SKU-001", "precio_venta": "1500.00", "stock_min_global": 10, "id_cat": 1, "descripcion": "..." }`

#### `PUT /api/inventario/productos/<id>/`
Edición de producto existente (US09).

#### `DELETE /api/inventario/productos/<id>/`
Elimina un producto. Si tiene stock o movimientos: retorna `400` con mensaje descriptivo (no `500`).

#### `GET /api/inventario/productos/<id>/stock/`
Stock del producto en todas las sucursales.

---

### 4.4 Movimientos de Stock

#### `POST /api/inventario/movimientos/` — Salida / Venta (US06)
```json
{ "tipo": "Salida", "cantidad": 2, "id_art": 1, "id_suc": 1, "motivo": "Venta en mostrador - Ticket #4920" }
```

#### `POST /api/inventario/movimientos/` — Traslado entre Sucursales (US06)
```json
{ "tipo": "Traslado", "cantidad": 10, "id_art": 1, "id_suc": 1, "id_suc_destino": 2, "motivo": "Reabastecimiento" }
```

#### `GET /api/inventario/movimientos/?id_suc=1&id_art=1&tipo=Traslado&ordering=-fecha_hora`
Historial y trazabilidad de movimientos.

---

## 5. Ejemplos de Implementación en Java 17 / Android (Retrofit)

### 5.1 Configuración Base de Retrofit

```java
// ApiClient.java
public class ApiClient {
    private static final String BASE_URL = "http://10.0.2.2:8000/api/"; // Emulador Android
    private static Retrofit retrofit;

    public static Retrofit getClient() {
        if (retrofit == null) {
            retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        }
        return retrofit;
    }
}
```

### 5.2 Interfaz ApiService (Retrofit)

```java
// ApiService.java
public interface ApiService {

    // --- Autenticación ---
    @POST("usuarios/login/")
    Call<LoginResponse> login(@Body LoginRequest body);

    @POST("usuarios/token/refresh/")
    Call<RefreshResponse> refreshToken(@Body RefreshRequest body);

    @GET("usuarios/me/")
    Call<UsuarioDto> getPerfil(@Header("Authorization") String token);

    @PATCH("usuarios/me/")
    Call<UsuarioDto> actualizarPerfil(
        @Header("Authorization") String token,
        @Body PerfilRequest body
    );

    @DELETE("usuarios/me/")
    Call<MensajeResponse> desactivarCuenta(@Header("Authorization") String token);

    @POST("usuarios/registro/")
    Call<MensajeResponse> registro(@Body RegistroRequest body);

    @POST("usuarios/contacto/")
    Call<MensajeResponse> enviarContacto(@Body ContactoRequest body);

    // --- Roles ---
    @GET("usuarios/roles/")
    Call<List<RoleDto>> getRoles(@Header("Authorization") String token);

    // --- Usuarios (admin) ---
    @GET("usuarios/")
    Call<List<UsuarioDto>> getUsuarios(@Header("Authorization") String token);

    @PUT("usuarios/{id}/")
    Call<UsuarioDto> editarUsuario(
        @Header("Authorization") String token,
        @Path("id") int id,
        @Body UsuarioRequest body
    );

    @DELETE("usuarios/{id}/")
    Call<MensajeResponse> desactivarUsuario(
        @Header("Authorization") String token,
        @Path("id") int id
    );

    // --- Inventario ---
    @GET("inventario/sucursales/")
    Call<List<SucursalDto>> getSucursales(@Header("Authorization") String token);

    @GET("inventario/sucursales/{id}/inventario/")
    Call<List<StockItemDto>> getInventarioSucursal(
        @Header("Authorization") String token,
        @Path("id") int idSuc,
        @Query("solo_con_stock") boolean soloConStock,
        @Query("search") String search
    );

    @GET("inventario/productos/")
    Call<List<ProductoDto>> buscarProductoPorCodigo(
        @Header("Authorization") String token,
        @Query("codigo") String codigo
    );

    @GET("inventario/productos/{id}/stock/")
    Call<List<StockItemDto>> getStockPorSedes(
        @Header("Authorization") String token,
        @Path("id") int idArt
    );

    // --- Movimientos ---
    @POST("inventario/movimientos/")
    Call<MovimientoDto> registrarMovimiento(
        @Header("Authorization") String token,
        @Body MovimientoRequest body
    );
}
```

### 5.3 DTOs principales

```java
// LoginResponse.java
public class LoginResponse {
    private int id;
    private String nombre, email, access, refresh, token;
    @SerializedName("es_admin")   private boolean esAdmin;
    @SerializedName("es_empleado") private boolean esEmpleado;
    // getters...
}

// StockItemDto.java — incluye codigo y precio para evitar peticiones extra
public class StockItemDto {
    @SerializedName("id_stock")        private int idStock;
    @SerializedName("id_art")          private int idArt;
    @SerializedName("id_suc")          private int idSuc;
    @SerializedName("nombre_producto") private String nombreProducto;
    @SerializedName("nombre_sucursal") private String nombreSucursal;
    @SerializedName("codigo_producto") private String codigoProducto;
    @SerializedName("precio_venta")    private String precioVenta;
    @SerializedName("cantidad_stock")  private int cantidadStock;
    @SerializedName("stock_min")       private int stockMin;

    // Alerta de umbral: el item está bajo stock mínimo
    public boolean esBajoStock() { return cantidadStock <= stockMin; }
    // getters...
}

// MovimientoRequest.java
public class MovimientoRequest {
    private String tipo;   // "Salida", "Traslado"
    private int cantidad;
    @SerializedName("id_art")         private int idArt;
    @SerializedName("id_suc")         private int idSuc;
    @SerializedName("id_suc_destino") private Integer idSucDestino; // null para Salida
    private String motivo;
    // constructor, getters...
}

// ContactoRequest.java
public class ContactoRequest {
    private String email, asunto, mensaje;
    // constructor, getters...
}
```

### 5.4 Uso típico desde una Activity/Fragment

```java
// Ejemplo: login y guardar sesión
ApiService api = ApiClient.getClient().create(ApiService.class);

api.login(new LoginRequest(email, password)).enqueue(new Callback<LoginResponse>() {
    @Override
    public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
        if (response.isSuccessful()) {
            LoginResponse data = response.body();
            // Guardar tokens en EncryptedSharedPreferences
            prefs.edit()
                .putString("access_token", data.getAccess())
                .putString("refresh_token", data.getRefresh())
                .putInt("user_id", data.getId())
                .putBoolean("es_admin", data.isEsAdmin())
                .putBoolean("es_empleado", data.isEsEmpleado())
                .apply();
            // Navegar al menú principal según rol
        } else if (response.code() == 403) {
            // Mostrar: "Cuenta pendiente de aprobación"
        }
    }
    @Override
    public void onFailure(Call<LoginResponse> call, Throwable t) { /* manejo de red */ }
});
```

---

## 6. Tabla de Endpoints por Historia de Usuario

| HU | Endpoint | Método |
| :--- | :--- | :--- |
| US01 — Login y menú | `/api/usuarios/login/` | POST |
| US02 — Selección de sucursal | `/api/inventario/sucursales/` | GET |
| US03 — Inventario + umbral | `/api/inventario/sucursales/<id>/inventario/` | GET |
| US04 — Contacto / Soporte | `/api/usuarios/contacto/` | POST |
| US05 — Alta de productos | `/api/inventario/productos/` | POST |
| US06 — Traslados y salidas | `/api/inventario/movimientos/` | POST |
| US07 — Registro de cuenta | `/api/usuarios/registro/` | POST |
| US08 — Gestión de usuarios | `/api/usuarios/`, `/api/usuarios/roles/` | GET, PUT, DELETE |
| US09 — Editar/eliminar productos | `/api/inventario/productos/<id>/` | PUT, DELETE |
| US12 — Perfil propio | `/api/usuarios/me/` | GET, PATCH |
| US11 — Baja de cuenta | `/api/usuarios/me/` | DELETE |
