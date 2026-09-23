# Architecture Decision Records (ADRs) — CodeLab_Stock

Este directorio contiene el registro histórico e inmutable de las decisiones arquitectónicas significativas tomadas a lo largo del ciclo de vida del proyecto.

---

## 1. Estructura y Formato

Cada ADR sigue el **formato Nygard** y se documenta en un archivo individual:

`Docs/ADR/NNNN-titulo-descriptivo.md`

### Estructura de Secciones Obligatorias:

1. **Título**: `# NNNN - Título conciso de la decisión`
2. **Estado**: Estado actual de la decisión (ver ciclo de vida abajo).
3. **Contexto**: Motivación técnica, problema a resolver y restricciones de diseño existentes.
4. **Decisión**: La solución técnica acordada y los cambios a implementar.
5. **Consecuencias**: 
   - Positivas (+).
   - Negativas / Trade-offs (-).
6. **Implementación / Notas**: Referencia a la rama, Pull Request o commit(s) donde se llevó a cabo el cambio para trazabilidad.

---

## 2. Ciclo de Vida y Estados Permitidos

Los ADRs registran decisiones de arquitectura, no el progreso del backlog:

- **`Propuesto`**: En discusión o evaluación técnica; aún no acordado definitivamente.
- **`Aceptado`**: Decisión aprobada por el equipo/desarrollador. *(Permanece en `Aceptado` permanentemente una vez implementada)*.
- **`Rechazado`**: Propuesta evaluada y descartada (preservada para documentar por qué no se eligió).
- **`Reemplazado` (Superseded)**: La decisión quedó superada por una nueva arquitectura (debe incluir enlace `Reemplazado por ADR-XXXX`).
- **`Obsoleto` (Deprecated)**: La funcionalidad o componente fue removido y la decisión ya no aplica.

---

## 3. Índice de Decisiones

| N° | Título | Estado | Implementación |
| :--- | :--- | :--- | :--- |
| **0001** | [Filtrado de movimientos: transición de cliente a servidor](./0001-filtrado-movimientos-servidor.md) | `Aceptado` | `feature/filtrado-server-side-movimientos` |
| **0002** | [Registro dual atómico para movimientos de tipo Traslado](./0002-registro-dual-traslados.md) | `Aceptado` | `feature/traslados-registro-dual` |
| **0003** | [Desacople semántico de Operador y Proveedor en Movimientos](./0003-desacople-operador-movimientos.md) | `Propuesto` | `feature/desacople-operador-movimientos` |
| **0004** | [Enforcement global de autenticación en la API REST](./0004-enforcement-global-autenticacion.md) | `Aceptado` | `feature/enforcement-autenticacion-api` |
| **0005** | [Sucursal Central y Distribución Jerárquica de Stock](./0005-sucursal-central-y-distribucion-jerarquica.md) | `Aceptado` | `feature/sucursal-central-distribucion` |
