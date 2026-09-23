# 0002 - Registro dual atómico para movimientos de tipo Traslado

## Estado

Aceptado

## Contexto

Un Traslado mueve stock de una sucursal origen a una sucursal destino. La implementación original registraba un único movimiento en la tabla `MOVIMIENTO`, asociado exclusivamente a la sucursal de origen, con un signo genérico (±) para representar la operación.

Esto generaba un defecto de comportamiento: al filtrar movimientos por sucursal destino (`?id_suc=B`), esa sucursal no veía ningún registro del traslado que acababa de recibir, pese a que su stock físico (`StockSucursal`) sí se había actualizado correctamente. El problema no era de cálculo de stock, sino de trazabilidad / auditoría: el movimiento existía físicamente pero no dejaba rastro visible desde la perspectiva de la sucursal receptora.

## Decisión

Un Traslado se representa mediante DOS registros de `Movimiento` vinculados semánticamente (no por FK explícita, sino por convención de motivo y timestamp), generados dentro de una misma transacción atómica (`transaction.atomic()`):

- Registro de egreso en origen: `id_suc = A`, `tipo = 'Traslado'`, `motivo = "Traslado hacia [Sucursal Destino]"`.
- Registro de ingreso en destino: `id_suc = B`, `tipo = 'Traslado'`, `motivo = "Recepción desde [Sucursal Origen]"`.

Ambos movimientos guardan su propio `stock_previo` (de origen y de destino respectivamente), y el débito/crédito de `StockSucursal` se ejecuta dentro de la misma transacción para evitar estados intermedios inconsistentes (stock descontado en A sin acreditar en B, o viceversa, si algo falla a mitad de camino).

## Consecuencias

Positivas:

- Cada sucursal ve su propio historial de movimientos completo al filtrar por `id_suc`, sin necesidad de lógica especial en el frontend para "adivinar" traslados que la involucran indirectamente.
- El registro es simétrico: origen y destino tienen la misma jerarquía de datos (cada uno con su `stock_previo`, su `motivo`), en vez de que uno sea "el movimiento real" y el otro un derivado.
- La atomicidad evita el escenario de stock fantasma (descontado en un lado, no acreditado en el otro) ante un fallo parcial.

Negativas / trade-offs:

- Un Traslado ya no es "un movimiento", son dos filas en la tabla. Cualquier reporte o cálculo que cuente movimientos totales tiene que tener en cuenta que un traslado cuenta doble, o filtrar por tipo+motivo para no duplicar en agregaciones.
- No hay FK explícita que vincule los dos registros entre sí (se infieren por tipo, timestamp y motivo). Si más adelante se necesita navegar de un lado al otro de forma confiable (por ejemplo, "deshacer un traslado"), esto puede requerir revisarse.
- Los tests (`test_traslados.py`) tienen que validar ambos lados de la operación en conjunto, no un movimiento aislado.

## Alternativas consideradas

Un único registro `Movimiento` con dos FKs (`sucursal_origen`, `sucursal_destino`) en vez de dos filas separadas. Se descartó porque hubiera requerido lógica adicional en el filtrado por sucursal (`id_suc = origen OR id_suc = destino`) tanto en el backend como en cualquier reporte futuro, y complica el modelo para el caso simple de Entrada/Salida que sí tiene una sola sucursal involucrada.

## Implementación

- **Rama**: `feature/traslados-registro-dual`
- **Componentes modificados**:
  - `Backend/inventario/views.py` (`MovimientoViewSet.create()`)
  - `Backend/inventario/test_traslados.py`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.ts`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.html`
