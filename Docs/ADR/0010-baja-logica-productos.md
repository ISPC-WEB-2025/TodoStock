# 0010 - Baja Lógica de Productos y Preservación de Trazabilidad

- **Estado**: `Propuesto`
- **Fecha**: 2026-10-12
- **Autor**: Equipo TodoStock
- **GitHub Issue**: [#322](https://github.com/ISPC-WEB-2025/TodoStock/issues/322)
- **Spec**: [`specs/016-baja-logica-productos.md`](../../specs/016-baja-logica-productos.md)

---

## 1. Contexto

En el sistema TodoStock, cada vez que se da de alta un producto en el catálogo (`POST /api/inventario/productos/`), se crean automáticamente registros de stock en cada sucursal existente (`StockSucursal`). Dichos registros, al igual que los movimientos históricos (`Movimiento`), establecen una restricción de clave foránea con protección de integridad (`on_delete=models.PROTECT`).

Debido a esto:
1. La operación actual de borrado físico (`DELETE /api/inventario/productos/{id}/`) siempre es bloqueada por la base de datos y Django, retornando un error `400 Bad Request` (`ProtectedError`). El producto nunca se puede eliminar.
2. Si se forzara el borrado en cascada (`CASCADE`), se destruirían los movimientos históricos de inventario, auditoría y balances contables de stock previo, violando la trazabilidad del sistema.
3. El modelo `Producto` actual carece de cualquier campo indicador de estado (`activo` o `estado`), y sus tablas en MariaDB/MySQL operan bajo `managed = False`.

---

## 2. Decisión

Implementar **baja lógica** para la entidad `Producto` preservando toda la estructura relacional e histórica:

1. **Esquema de Base de Datos:**
   - Incorporar la columna `activo BOOLEAN NOT NULL DEFAULT TRUE` a la tabla `PRODUCTO` en los scripts de inicialización (`Backend/scripts/todostock_db.sql`) y en la base productiva mediante `ALTER TABLE`.
   - Mapear el campo `activo` en el modelo `Producto` (`Backend/inventario/models.py`) y en `ProductoSerializer`.

2. **Comportamiento del Endpoint `DELETE`:**
   - La acción `DELETE /api/inventario/productos/{id}/` (restringida a Administradores) dejará de intentar un borrado físico (`model.delete()`). En su lugar, modificará el estado a `activo = False` y responderá HTTP `204 No Content`.

3. **Filtrado y Visibilidad:**
   - En el backend, las consultas habituales de catálogo (`/api/inventario/productos/`), productos por categoría (`/api/inventario/categorias/{id}/productos/`) y disponibilidad en inventario excluirán por defecto los registros con `activo = False`.
   - Se mantendrán accesibles únicamente en consultas de auditoría o históricos mediante filtros explícitos si fuera requerido.

4. **Reglas Operativas:**
   - Se prohíbe la generación de nuevos movimientos de stock (`Entrada`, `Salida`, `Traslado`) con productos dados de baja (`activo = False`), respondiendo HTTP `400 Bad Request`.
   - El código SKU/alfanumérico de un producto dado de baja permanece ocupado (no reutilizable) por mantener la unicidad de clave en la base de datos y evitar colisiones históricas.

---

## 3. Consecuencias

### Positivas (+)
- **Trazabilidad intacta:** Todos los movimientos pasados (`Movimiento`) y registros de stock conservan su referencia íntegra sin romper claves foráneas.
- **Resolución del bloqueo de `DELETE`:** El frontend web y la aplicación móvil pueden invocar la eliminación sin recibir rechazos por `ProtectedError`.
- **Desacople limpio:** La app móvil y web simplemente dejan de ver productos discontinuados u obsoletos en la operativa diaria.

### Negativas / Trade-offs (-)
- **Migración manual requerida:** Como `managed = False`, requiere aplicar el `ALTER TABLE PRODUCTO ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;` en la base de datos externa (Alwaysdata).
- **Códigos únicos bloqueados:** Un código de producto dado de baja no podrá reutilizarse a menos que se implemente una lógica más compleja de unicidad compuesta o sufijos.

---

## 4. Implementación y Notas

- Rama de trabajo prevista: `feature/baja-logica-productos-322`
- Script de migración en producción:
  ```sql
  ALTER TABLE PRODUCTO ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
  ```
- Spec asociada: `specs/016-baja-logica-productos.md`
