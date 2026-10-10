# 0009 - Modelo de Log de Auditoría Desacoplado y Registro de Eventos de Seguridad

## Estado

Aceptado

## Contexto

En el marco del endurecimiento de seguridad y trazabilidad operativa (US14 / RNF-SEG / TK51), el sistema requiere registrar eventos críticos de seguridad (altas, bajas, inicios de sesión correctos y fallidos, cambios de rol, movimientos y bloqueos por fuerza bruta). 

Específicamente, surgen las siguientes necesidades inmediatas:
1. **Validación de Derecho a Baja y Legislación (TK59 / TC-SEG-05 / TK52):** Al ejercer el derecho de autoservicio para desactivar una cuenta propia (`DELETE /api/usuarios/me/`), el sistema debe generar evidencia fehaciente e inmutable del evento con fecha, usuario y acción realizada.
2. **Control de Intrusiones y Fuerza Bruta (TK58 / Pedro):** Al superarse el umbral de intentos fallidos de autenticación, el bloqueo temporal debe quedar registrado para auditoría.
3. **Resiliencia y Desacople de Datos:** Si un registro de auditoría dependiera estrictamente de una clave foránea activa y obligatoria (`NOT NULL`) a la tabla `Usuario`, fallaría ante intentos de autenticación con correos inexistentes o ante usuarios desactivados/anonimizados. Por ende, la persistencia del log debe ser independiente de la existencia o estado del usuario en la base de datos.
4. **Consulta Segura:** Los registros de auditoría no deben ser modificables por ningún operador y solo deben ser consultables por usuarios con perfil `ADMINISTRADOR`.

## Decisión

1. **Creación del Modelo `LogAuditoria` en `usuarios`**:
   Se define en `Backend/usuarios/models.py` la entidad `LogAuditoria` con los siguientes atributos:
   - `fecha_hora`: `DateTimeField(auto_now_add=True, db_index=True)` — Timestamp inmutable de la ocurrencia.
   - `usuario`: `ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='logs_auditoria')` — Enlace relacional cuando el usuario existe.
   - `usuario_email`: `CharField(max_length=254, db_index=True)` — Identificador de texto plano que garantiza conservar la traza aunque el usuario sea anonimizado o no exista en el sistema (ej. intentos de login fallido).
   - `evento`: `CharField(max_length=50, choices=...)` — Código estructurado del evento (`BAJA_CUENTA`, `LOGIN_EXITOSO`, `LOGIN_FALLIDO`, `BLOQUEO_FUERZA_BRUTA`, `ALTA_USUARIO`, `CAMBIO_ROL`, `MOVIMIENTO_STOCK`).
   - `descripcion`: `TextField(blank=True)` — Contexto adicional (motivo, detalle del cambio, estado previo).
   - `ip_origen`: `GenericIPAddressField(null=True, blank=True)` — Dirección IP del cliente remitente de la solicitud HTTP.

2. **Helper Centralizado `registrar_auditoria`**:
   Se encapsula la creación de logs en una función utilitaria (`usuarios/services.py` o `usuarios/utils.py`). El helper:
   - Extrae automáticamente la IP de la solicitud HTTP (`request`).
   - Tolera llamadas con `user` anónimo o inexistente extrayendo el email suministrado.
   - Envuelve la persistencia en un bloque de control de errores para garantizar que una eventual falla al escribir el log nunca interrumpa ni degrade la transacción operativa principal del usuario.

3. **Instrumentación del Evento de Baja (`DELETE /api/usuarios/me/`)**:
   En `UserViewSet.me`, una vez desactivada la cuenta (`is_active = False`), se invoca `registrar_auditoria` con el evento `BAJA_CUENTA`, usuario y su email.

4. **Acceso Exclusivo de Administrador**:
   - **Django Admin:** Se expone `LogAuditoriaAdmin` en `usuarios/admin.py` configurado con `has_add_permission=False` y `has_change_permission=False` para prevenir alteración o falsificación manual de los registros históricos.
   - **API REST:** Se habilita el endpoint `GET /api/usuarios/auditoria/` restringido a roles administrativos (`EsAdminParaModificar` / `es_admin == True`).

## Consecuencias

### Positivas (+)
- **Conformidad Normativa y Testing:** Proporciona la evidencia requerida por el caso de prueba TC-SEG-05 (TK59) y formaliza la tabla de auditoría estipulada en la issue TK51.
- **Preparación para Fuerza Bruta:** Deja disponible la infraestructura para que el módulo de throttling (TK58) registre intentos bloqueados sin necesidad de nuevas migraciones.
- **Inmutabilidad y Seguridad:** El desacople mediante `usuario_email` y `SET_NULL` previene pérdida de trazas por eliminación de cuentas y los permisos de solo lectura resguardan la integridad de la auditoría.
- **Cero Impacto en Datos Previos:** Es una tabla completamente aditiva que no modifica el esquema de las tablas de inventario ni de usuarios existentes.

### Negativas / Trade-offs (-)
- **Crecimiento de Almacenamiento:** Los registros crecen linealmente con el uso del sistema; a mediano plazo requerirá políticas de retención o archivado (rotación semestral/anual).

## Implementación / Notas

- Rama: `feature/log-auditoria-seguridad`
- Tareas asociadas: `#TK51`, `#TK59`, `#TK58`
- GitHub Issue: `#316`
