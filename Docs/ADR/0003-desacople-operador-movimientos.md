# 0003 - Desacople semántico de Operador y Proveedor en Movimientos de Inventario

## Estado

Propuesto

## Contexto

En la pantalla de trazabilidad de movimientos de inventario (`Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.html`), existía una única columna titulada ambiguamente *"Proveedor / Remitente"*, respaldada en el modelo relacional únicamente por el campo `id_prov` (Foreign Key hacia la tabla `PROVEEDOR`).

Esta sobrecarga generaba una ambigüedad semántica y de dominio:
1. `id_prov` solo aplica para movimientos de tipo **Entrada** (adquisición a un proveedor externo).
2. Para movimientos de **Traslado**, **Salida** o **Merma**, el rótulo *"Remitente"* inducía al error de interpretar que allí debía figurar qué sucursal transfirió la mercadería o qué empleado ejecutó la acción.
3. El campo `id_prov` no puede reutilizarse para persistir nombres de usuarios o sucursales debido a que es una Clave Foránea estricta en MySQL (`INTEGRITY CONSTRAINT`), arrojando un error `IntegrityError (1452)` ante cualquier identificador ajeno a la tabla `PROVEEDOR`.

En el dominio coexisten tres entidades distintas:
- **Operador**: El usuario del sistema que ejecutó y firmó la operación (`id_usuario` $\rightarrow$ `usuarios_usuario.nombre`).
- **Proveedor**: La entidad comercial externa que abasteció el stock (`id_prov` $\rightarrow$ `PROVEEDOR.nombre`, exclusivo de compras/entradas).
- **Sucursales Origen / Destino**: Las dependencias físicas internas entre las que circula el stock (`id_suc` y detalle de destino/origen en `motivo`, resuelto a nivel transaccional en el [ADR 0002](./0002-registro-dual-traslados.md)).

*Nota de Alcance*: El manejo de sucursal origen/destino y su trazabilidad bidireccional quedó formalizado y desacoplado mediante el registro dual atómico en [ADR 0002](./0002-registro-dual-traslados.md). Esta decisión resuelve específicamente la separación entre **Operador** y **Proveedor**.

## Decisión

Separar explícitamente las entidades de **Operador** y **Proveedor** tanto en el Serializer de Django REST Framework como en la interfaz de usuario de Angular:

1. **Exposición en Serializer de Django**:
   - Incorporar el campo de solo lectura `nombre_usuario` en `Backend/inventario/serializers.py` (`MovimientoSerializer`):
     ```python
     nombre_usuario = serializers.CharField(
         source="id_usuario.nombre", read_only=True, default=None
     )
     ```
2. **Claridad de Dominio en UI (Angular)**:
   - Renombrar la columna *"Proveedor / Remitente"* a estrictamente **`"Proveedor"`**, renderizando el badge 🏢 únicamente cuando el movimiento sea de tipo Entrada (o exista `nombre_proveedor`).
   - Incorporar una columna independiente **`"Operador"`** (o *"Registrado por"*) que exhiba el badge 👤 `mov.nombre_usuario` en todos los movimientos (Entrada, Salida, Traslado y Merma).
   - Actualizar el modelo de interfaz en `Frontend/app-stock/src/app/core/models/movimiento.model.ts` incorporando la propiedad opcional `nombre_usuario?: string`.

## Alternativas Consideradas

- **Reutilizar el campo `id_prov` para almacenar identificadores de usuario o sucursal**:
  - *Descartada*: Inviable a nivel relacional debido a las restricciones de integridad referencial (`FOREIGN KEY`) de MySQL, además de violar el principio de responsabilidad única de la tabla `PROVEEDOR`.
- **Ocultar dinámicamente la columna Proveedor según el filtro de tipo de movimiento**:
  - *Descartada*: En vistas generales que listan todos los movimientos combinados, genera saltos y desalineación en el layout de la grilla. Se prefiere mantener columnas fijas con renderizado condicional de badges o celdas vacías (`—`).

## Consecuencias

Positivas:
- **Eliminación de la ambigüedad**: Cada columna en la tabla representa exactamente una entidad del modelo relacional (`Usuario` vs `Proveedor`).
- **Aprovechamiento de datos existentes**: El campo `id_usuario` ya se persiste automáticamente en cada request tras el enforcement de autenticación ([ADR 0004](./0004-enforcement-global-autenticacion.md)); este cambio solo lo expone en el DTO sin requerir migraciones de esquema SQL.
- **Protección de Integridad**: Evita cualquier intento de forzar `id_prov` fuera de su propósito natural.

Negativas / Trade-offs:
- Añade una columna adicional a la tabla de movimientos en Angular, requiriendo validación responsive en pantallas medianas y móviles.

## Implementación

- **Rama Planificada**: `feature/desacople-operador-movimientos`
- **Componentes a modificar**:
  - `Backend/inventario/serializers.py` (`MovimientoSerializer:L212-L243`)
  - `Frontend/app-stock/src/app/core/models/movimiento.model.ts:L7-L27`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.html`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.ts`
