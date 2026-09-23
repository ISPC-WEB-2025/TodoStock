# 0005 - Sucursal Central y Distribución Jerárquica de Stock

## Estado
Aceptado

## Contexto
El modelo original de la base de datos trataba a todas las entidades `SUCURSAL` de forma homogénea y plana. Sin embargo, en el dominio del negocio (distribuidora e inventario de perfiles y accesorios):
1. Las compras a proveedores con remitos de abastecimiento no se entregan indistintamente en cualquier punto de venta satélite, sino que ingresan a una **Sede Central / Fábrica Principal / Centro de Distribución**.
2. Los puntos de venta o depósitos satélite se nutren exclusivamente a través de **Traslados internos** originados desde dicha Sede Central o entre dependencias.
3. Al inicializar un producto nuevo, su `stock_min_global` (que representa el punto de reorden de compra para toda la compañía) se clonaba idénticamente como `stock_min` local de cada sede. Como consecuencia, sedes satélites quedaban en alerta roja constante ("Sin Existencias" o "Stock Bajo") a pesar de no requerir ese nivel de existencias mínimas.

## Decisión
1. **Atributo `es_central` en `SUCURSAL`**:
   Se agrega el campo booleano `es_central` (`BOOLEAN NOT NULL DEFAULT FALSE`) a la tabla `SUCURSAL`. Por convención inicial, la "Fábrica Principal" se define con `es_central = True`.
2. **Restricción de Compras a Proveedores (Entradas)**:
   A nivel de lógica de negocio y API (`MovimientoViewSet`), toda operación de tipo `Entrada` debe recibirse obligatoriamente en una sucursal con `es_central = True`. Cualquier intento de registrar una compra directa de proveedor en un punto de venta satélite es rechazado con error HTTP 400.
3. **Distribución mediante Traslados**:
   Los puntos de venta obtienen su stock físico mediante movimientos de tipo `Traslado` desde la Sede Central.
4. **Desacople de Umbrales**:
   Al crear un producto o dar de alta una sucursal, el umbral local (`stock_min`) en `STOCK_SUCURSAL` se inicializa en `0` (quedando sujeto al ajuste in-situ que realice el encargado del local) en lugar de duplicar el `stock_min_global`.
5. **Auto-promoción de la primera sede y garantía de unicidad**:
   Al crear una sucursal, si no existe ninguna otra sede en el sistema con `es_central = True`, el sistema la promueve automáticamente como Casa Central. Cuando se designa una nueva sucursal como central, el backend actualiza atómicamente la sede anterior para garantizar que siempre exista exactamente una Casa Central activa.
6. **Blindaje contra eliminación de la Casa Central**:
   No se permite la eliminación de una sucursal mientras posea el rol de Casa Central (`es_central = True`). Para poder eliminarla, el administrador debe designar previamente otra sucursal existente como Casa Central y vaciar sus existencias físicas y registros.

## Consecuencias
### Positivas (+)
- **Modelado fidedigno del negocio:** Se respeta la cadena logística real de compras mayoristas y distribución capilar.
- **Limpieza visual y operativa:** Los puntos de venta satélites no muestran alertas falsas ni reciben remitos de compra externos por error.
- **Auditoría centralizada:** La mercadería ingresa por el nodo central, facilitando el control de remitos de proveedores.

### Negativas / Trade-offs (-)
- Requiere que al menos una sucursal esté designada como central en la base de datos para poder registrar entradas de compras.

## Implementación / Notas
- **Rama:** `feature/sucursal-central-distribucion`
- **Archivos:**
  - SQL: `Backend/scripts/01_estructura.sql`, `Backend/scripts/todostock_db.sql`, `Backend/scripts/03_datos.sql`.
  - Backend: `Backend/inventario/models.py`, `Backend/inventario/serializers.py`, `Backend/inventario/views.py`.
  - Frontend: `Frontend/app-stock/src/app/core/models/sucursal.model.ts`, componentes de sucursales y movimientos.
