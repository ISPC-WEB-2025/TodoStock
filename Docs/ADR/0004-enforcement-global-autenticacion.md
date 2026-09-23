# 0004 - Enforcement global de autenticación en la API REST

## Estado

Aceptado

## Contexto

`REST_FRAMEWORK` en `Backend/config/settings.py` no definía `DEFAULT_PERMISSION_CLASSES`, por lo que Django REST Framework operaba bajo `AllowAny` por omisión en todos los ViewSets y APIViews que no declararan permisos explícitamente.

Se detectó a raíz de una auditoría sobre el campo `id_usuario` en la entidad `Movimiento` (campo nullable con asignación dependiente de `request.user.is_authenticated`), lo que permitía que peticiones sin header `Authorization` insertaran registros anónimos (`id_usuario = NULL`), comprometiendo la trazabilidad del sistema.

La auditoría completa del backend determinó que todos los ViewSets del inventario (`ProductoViewSet`, `CategoriaViewSet`, `SucursalViewSet`, `ProveedorViewSet`, `ProductoProveedorViewSet`, `StockSucursalViewSet`, `MovimientoViewSet`) y el catálogo de vendedores (`ProductoVendedorView`) se encontraban expuestos sin requerir token.

En el frontend (`Frontend/app-stock/src/app/core/interceptors/auth.interceptor.ts`), se constató que la exclusión de endpoints públicos opera mediante `req.url.includes(...)` (L13-L16) para `/api/usuarios/login/`, `/api/usuarios/registro/` y `/api/usuarios/token/refresh/`, y se implementa un circuito de corte ante errores 401 en el endpoint de refresh para evitar bucles infinitos de reintentos y disparar el logout (L33-L38 y L67-L72).

## Decisión

Adoptar el principio arquitectónico **"seguro por defecto, público por excepción"**:

1. Configurar `'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']` globalmente en `REST_FRAMEWORK` dentro de `Backend/config/settings.py`.
2. Aplicar override explícito `permission_classes = [AllowAny]` únicamente en los endpoints públicos de autenticación: `LoginUsuarioView` y `RegistroUsuarioView` en `Backend/usuarios/views.py`, mientras `TokenRefreshView` opera bajo su configuración nativa de SimpleJWT.
3. Incorporar una suite de pruebas automatizadas en backend (`Backend/inventario/test_auth_enforcement.py`) para validar formalmente el rechazo con `HTTP 401 Unauthorized` ante peticiones anónimas a todos los endpoints de negocio, y el acceso concedido (`HTTP 200/201`) con credenciales válidas.
4. Incorporar pruebas unitarias en frontend (`Frontend/app-stock/src/app/core/interceptors/auth.interceptor.spec.ts`) para verificar que un error 401 durante el refresco de token ejecute `authService.logout()` una única vez y corte la cadena sin generar loops de reintento.

## Alternativas Consideradas

- **Permisos explícitos `permission_classes = [IsAuthenticated]` caso por caso en cada ViewSet / APIView**:
  - *Descartada*: Modelo de seguridad "opt-in" propenso a fallas humanas. Si un desarrollador olvida declarar `permission_classes` en un nuevo ViewSet, DRF lo expone públicamente bajo `AllowAny` por omisión.
  - *Ventaja del enfoque elegido*: "Seguro por defecto" garantiza que cualquier nuevo endpoint o ViewSet que se añada a la aplicación nace protegido por JWT automáticamente.

## Consecuencias

Positivas:
- **Seguridad Integral**: Todo nuevo ViewSet, APIView o endpoint que se incorpore al backend nacerá automáticamente protegido por autenticación JWT, eliminando el riesgo de omisiones accidentales.
- **Garantía de Auditoría**: Asegura que las operaciones de inventario y movimientos siempre cuenten con un usuario autenticado, garantizando que `id_usuario` registre al responsable de cada acción.
- **Consistencia con Frontend**: Se alinea con el `authInterceptor` de Angular que ya adjunta `Bearer <token>` en todas las peticiones salientes.

Negativas / Trade-offs:
- Clientes externos o scripts de prueba que operaban sin token deberán autenticarse previamente en `/api/usuarios/login/` para consumir la API.
- La exclusión de endpoints públicos en `authInterceptor` (`Frontend/app-stock/src/app/core/interceptors/auth.interceptor.ts:L13-L16`) usa `String.prototype.includes()` (coincidencia por substring) y no coincidencia exacta. **Riesgo/Consideración aceptada**: Cualquier endpoint futuro cuya URL contenga alguno de esos paths como substring quedaría excluido de la inyección de `Bearer <token>` de forma no intencional.

## Verificación de Pendientes de Auditoría

1. **Exclusión de endpoints en Frontend**: Documentado el uso de `String.includes` como riesgo aceptado (`auth.interceptor.ts:L13-L16`).
2. **Circuito de corte ante doble 401 en refresh**: Verificado formalmente mediante prueba unitaria en `Frontend/app-stock/src/app/core/interceptors/auth.interceptor.spec.ts:L66-L91`, confirmando que un error 401 en `/token/refresh/` dispara `authService.logout()` exactamente 1 sola vez y corta la cadena de observables sin reintentos infinitos.
3. **Rechazo 401 en peticiones anónimas**: Verificado en backend mediante `Backend/inventario/test_auth_enforcement.py:L1-L168` cubriendo productos, categorías, sucursales, proveedores, stock, movimientos y catálogo de vendedor.

## Notas sobre Datos Existentes

- Los movimientos generados previamente en entornos de desarrollo/pruebas con `id_usuario = NULL` quedan documentados como registros históricos de testing previos al enforcement global de seguridad.

## Implementación

- **Rama**: `feature/enforcement-autenticacion-api`
- **Componentes modificados**:
  - `Backend/config/settings.py` (`REST_FRAMEWORK:L129-L138`)
  - `Backend/usuarios/views.py` (`LoginUsuarioView:L37-L40`)
  - `Backend/inventario/test_auth_enforcement.py`
  - `Frontend/app-stock/src/app/core/interceptors/auth.interceptor.spec.ts`
