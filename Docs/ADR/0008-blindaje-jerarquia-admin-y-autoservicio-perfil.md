# 0008 - Blindaje de jerarquía administrativa, autoservicio de perfil y aprovisionamiento de superusuario

## Estado

Aceptado

## Contexto

A través de la auditoría de autenticación y de las pruebas operativas en entornos locales y remotos se identificaron tres problemáticas críticas en la gestión de usuarios y seguridad:

1. **Vulnerabilidad de Admin vs Admin y falta de jerarquía:**
   En `UserViewSet` (`Backend/usuarios/views.py`), el permiso `EsAdminParaModificar` solo validaba `request.user.es_admin` a nivel general. En consecuencia, cualquier usuario con rol `ADMINISTRADOR` podía enviar un `PUT /api/usuarios/<id>/` (incluso alterando el campo `password`) sobre cualquier otra cuenta, incluyendo otros administradores o el superusuario (`is_superuser`), sin confirmación de clave actual ni trazabilidad.
2. **Falta de visibilidad de `is_superuser` en clientes:**
   Ni `UsuarioSerializer` ni el endpoint `/api/usuarios/me/` exponían el flag `is_superuser`. Por ende, el frontend (Web y Mobile) no podía diferenciar visualmente al Administrador Principal del resto de administradores ni condicionar la habilitación de los botones de edición y desactivación.
3. **Bloqueo del autoservicio de perfil:**
   Los usuarios operativos (`EMPLEADO`) no podían actualizar sus propios datos personales (nombre, fecha de nacimiento) porque `UserViewSet` rechazaba peticiones de usuarios no administradores con `403 Forbidden`, y el endpoint `/api/usuarios/me/` admitía únicamente `GET` (solo lectura).
4. **Fragilidad en la creación del superusuario por defecto (Local vs Remoto):**
   El script `Backend/setup_db.py` ejecuta la creación del superadmin como paso final acoplado. Si ocurrían fallos previos en scripts SQL o colisiones en campos únicos (ej. DNI fijo `12345678` preexistente), el usuario por defecto de desarrollo (`admin@codelab.com` / `AdminPassword123!`) no se creaba o quedaba en un estado inconsistente en local.

## Decisión

1. **Jerarquía Estricta y Protección Admin vs Admin**:
   - Se incorpora control de permisos a nivel de objeto (`has_object_permission`): **Únicamente el Super Administrador (`request.user.is_superuser == True`) puede crear, editar, reasignar rol o desactivar cuentas con rol `ADMINISTRADOR` o `is_superuser`**.
   - Cualquier intento de un administrador regular de modificar o resetear credenciales de otro administrador es bloqueado con código `HTTP 403 Forbidden` (*"Acción reservada al Super Administrador"*).
   - Ningún usuario puede degradar o desactivar la cuenta del superusuario raíz.

2. **Exposición de `is_superuser` y Leyenda Distintiva en UI**:
   - `UsuarioSerializer` y `/api/usuarios/me/` exponen `is_superuser` como campo de solo lectura (`read_only=True`).
   - En la interfaz de usuarios (Web y Mobile), se establece una distinción visual inequívoca:
     * Para `is_superuser`: Badge destacado con leyenda **`Super Admin`** o **`Administrador Principal`** (con distintivo visual/escudo).
     * Para administradores estándar: Badge **`Administrador`**.
   - En la grilla de usuarios, para un admin regular los botones de acción ("Editar", "Desactivar") en las filas de otros administradores se muestran deshabilitados con tooltip explicativo.

3. **Desacople del Cambio de Contraseña**:
   - Se elimina la modificación directa de contraseñas desde el endpoint general `PUT /api/usuarios/<id>/`.
   - Se define un endpoint específico de autoservicio: `POST /api/usuarios/me/change-password/`, requiriendo obligatoriamente `password_actual`, `nueva_password` y respetando las políticas de complejidad.
   - El reseteo administrativo de empleados se canaliza mediante un endpoint dedicado (`POST /api/usuarios/<id>/reset-password/`), restringido a cuentas de rol no administrativo.

4. **Autoservicio de Perfil de Usuario**:
   - Se habilitan los métodos `PATCH` y `PUT` en `/api/usuarios/me/` consumiendo un serializer restringido (`PerfilUsuarioSerializer`).
   - El usuario puede editar sus datos personales (`nombre`, `fecha_nacimiento`), pero la API bloquea y descarta intentos de auto-modificar campos sensibles (`rol_id`, `email`, `is_active`, `is_staff`, `is_superuser`).

5. **Aprovisionamiento Robusto de Superusuario (Local vs Remoto)**:
   - En desarrollo local (`DEBUG=True`), se garantiza la idempotencia de `crear_superadmin.py`: si el usuario `admin@codelab.com` existe, se sincronizan sus permisos (`is_superuser=True`, `is_staff=True`, `is_active=True`, rol `ADMINISTRADOR`) y contraseña conocida sin colisionar con DNI.
   - Se desacopla la ejecución de `crear_superadmin.py` como comando independiente (`manage.py` / script standalone) para que el desarrollador pueda re-aprovisionar o reparar el superadmin local sin requerir reiniciar la base de datos completa.
   - En entornos remotos (`DEBUG=False`), se prioriza la configuración de variables de entorno (`ADMIN_EMAIL`, `ADMIN_PASSWORD`), manteniendo la autogeneración aleatoria como fallback seguro.

## Consecuencias

### Positivas (+)
- **Seguridad y Jerarquía Claras:** Cierre de riesgos de toma de control (takeover) entre cuentas administradoras y protección del superusuario raíz.
- **Claridad de Interfaz (UX):** El personal visualiza claramente los niveles de autorización mediante leyendas diferenciadas.
- **Autonomía Operativa:** Empleados y vendedores pueden actualizar su perfil desde la web o la app móvil sin requerir soporte administrativo.
- **Entorno de Desarrollo Estable:** Asegura que en local siempre se cuente con el superadmin funcional con las credenciales documentadas.

### Negativas / Trade-offs (-)
- Los administradores regulares ya no pueden resetear contraseñas de otros administradores en caso de olvido; dicha acción recae exclusivamente en el Super Administrador.
- Requiere endpoints y serializers adicionales para separar la actualización de perfil y la gestión de contraseñas.

## Implementación / Notas

- **Archivos de Referencia:**
  - Backend: `Backend/usuarios/views.py`, `Backend/usuarios/serializers.py`, `Backend/usuarios/models.py`, `Backend/scripts/crear_superadmin.py`.
  - Frontend: `Frontend/app-stock/src/app/features/lista-usuarios/`, `Frontend/app-stock/src/app/core/services/usuario.service.ts`.
  - Backlog: Relacionado con Issues #261, #286 y #287.
