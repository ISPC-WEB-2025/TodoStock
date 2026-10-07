# 0006 - Arquitectura de consumo del Backend por Aplicación Mobile

## Estado

Aceptado

## Contexto

El sistema de inventario y stock operaba inicialmente con un único cliente frontend web (SPA en Angular). Ante la necesidad operativa de agilizar el control de existencias en salón y depósito (conteo in-situ, recepción rápida de mercadería, transferencias entre sedes y escaneo de códigos de barra / QR desde la cámara del dispositivo), se decidió incorporar una aplicación móvil nativa/híbrida (Android / Flutter).

Para evitar la duplicación de lógica de negocio o la creación de un backend paralelo exclusivo para móviles (BFF innecesario para la escala actual), se requirió evaluar la preparación y adaptación de la API REST construida sobre Django REST Framework (DRF) para ser consumida de manera eficiente y segura por clientes móviles.

## Decisión

1. **Reutilización de la API REST y Contrato Unificado**:
   El backend expone la misma arquitectura REST para el cliente web y la app móvil, garantizando consistencia en las reglas de validación de negocio y persistencia en MySQL.

2. **Autenticación Stateless vía JWT**:
   La autenticación móvil opera íntegramente mediante JSON Web Tokens (`rest_framework_simplejwt`), inyectando el header estándar `Authorization: Bearer <access_token>` en cada solicitud:
   - El dispositivo almacena de manera segura los tokens (`access` y `refresh`) en almacenamiento cifrado del dispositivo (Keystore/Key环 en Android / iOS Secure Storage).
   - El refresco de credenciales se canaliza por `/api/usuarios/token/refresh/` cuando el token de acceso expira.

3. **Endpoint de Perfil de Usuario (`/api/usuarios/me/`)**:
   Se incorpora la acción `@action(detail=False, methods=['get'])` en `UserViewSet` para que la aplicación móvil obtenga los datos del usuario autenticado, su rol y banderas operativas (`es_admin`, `es_empleado`) tras el inicio de sesión, sin requerir almacenar estado redundante.

4. **Optimización para Lectores Ópticos y Búsqueda Rápida**:
   En `ProductoViewSet`, se habilita el filtro exacto por código (`/api/productos/?codigo=<codigo>`), optimizado para búsquedas instantáneas disparadas por lectores de código de barras o escaneo de cámara.

5. **Filtros Granulares en Movimientos y Stock**:
   En `MovimientoViewSet` y `StockSucursalViewSet`, se habilitan filtros por sucursal, producto y tipo de movimiento para evitar la descarga de grandes volúmenes de datos sobre conexiones de red móviles de ancho de banda variable.

6. **Permisividad de Conexiones de Red y Emuladores**:
   Se configuran `CORS_ALLOW_ALL_ORIGINS` y soporte en `ALLOWED_HOSTS` para habilitar peticiones desde emuladores de desarrollo (`10.0.2.2` en emulador Android) y dispositivos físicos en redes locales o despliegues remotos.

7. **Documentación de Integración Móvil**:
   Se establece el catálogo de contratos y ejemplos de integración técnica (en Flutter y Android Retrofit) centralizado en `Docs/API_MOBILE.md`.

## Consecuencias

### Positivas (+)
- **Backend Agnóstico**: No se requiere mantener código ni servidores separados para la aplicación móvil.
- **Seguridad Robusta**: Se aprovecha el enforcement global de autenticación JWT (ADR-0004) asegurando que cada movimiento quede imputado al operador correspondiente.
- **Rendimiento Móvil**: Filtros específicos por código de barras y sucursal que minimizan el consumo de batería y datos móviles.
- **Documentación Centralizada**: Facilita la incorporación de desarrolladores móviles al proyecto mediante especificaciones claras en `Docs/API_MOBILE.md`.

### Negativas / Trade-offs (-)
- La aplicación móvil debe implementar la lógica de interceptor para renovación transparente de tokens y manejo del ciclo de vida offline/online.
- El escaneo continuo requiere índices optimizados en base de datos sobre la columna `codigo` de productos.

## Implementación / Notas

- **Rama:** `feature/mobile-api-readiness`
- **Archivos:**
  - Backend: `Backend/config/settings.py`, `Backend/inventario/views.py`, `Backend/usuarios/views.py`, `Backend/inventario/test_mobile_api.py`.
  - Documentación: `Docs/API_MOBILE.md`.
