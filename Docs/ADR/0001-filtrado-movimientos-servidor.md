# 0001 - Filtrado de movimientos: transición de cliente a servidor

## Estado

Aceptado

## Contexto

El sistema maneja un inventario distribuido en múltiples sucursales (tabla `STOCK_SUCURSAL`), donde cada movimiento (`Entrada`, `Salida`, `Traslado`) queda asociado a una sucursal de origen (`id_suc`). A medida que el volumen de movimientos crece, la pantalla de listado necesita poder filtrar por sucursal sin degradar el rendimiento ni sobrecargar al cliente con transferencias de datos innecesarias.

El backend (`MovimientoViewSet.get_queryset()`) ya soporta filtrado server-side vía query parameters (`?id_suc=X&tipo=Y`), pero esta capacidad no se estaba utilizando: el frontend (`MovimientoService.getAll()`) solicitaba la colección completa y el filtrado se resolvía en memoria mediante un getter reactivo en `ListaMovimientosComponent` (`movimientosFiltrados`). Esta inconsistencia no fue una decisión deliberada, sino el resultado de desarrollos asincrónicos entre backend y frontend sin retomar la integración completa.

## Decisión

Se decide migrar el filtrado de movimientos de client-side a server-side, aprovechando los parámetros ya existentes en la API REST de Django:

- El frontend deja de solicitar la colección completa sin filtros y envía los filtros activos (`id_suc`, `tipo`, `id_art`) como query parameters en cada petición mediante `HttpParams`.
- El estado de filtro (sucursal seleccionada) se mantiene en el componente Angular y dispara una recarga (`cargarMovimientos()`) en cada cambio, reemplazando el cálculo sobre la colección en memoria.
- Se gestiona un estado de carga visual (`cargando = true`) para proporcionar feedback fluido durante las peticiones asincrónicas.

## Consecuencias

Positivas:

- Menor volumen de datos transferidos y procesados en el cliente, optimizando el consumo de red a medida que crece el historial.
- El backend queda como única fuente de verdad para la lógica de filtrado y consultas de inventario.
- Prepara el terreno para la futura incorporación de paginación server-side (`PageNumberPagination`).

Negativas / Trade-offs:

- Se reemplaza la reactividad instantánea del filtrado en memoria por una petición asincrónica de red con latencia controlada.
- Requiere el manejo explícito de estados de carga (`cargando`) en la UI durante cada refetch.

## Implementación

- **Rama**: `feature/filtrado-server-side-movimientos`
- **Componentes modificados**:
  - `Frontend/app-stock/src/app/core/services/movimiento.service.ts`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.ts`
  - `Frontend/app-stock/src/app/features/vendedor/movimientos/lista-movimientos.component.html`
