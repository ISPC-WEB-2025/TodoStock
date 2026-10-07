# 0007 - Unificación operativa de roles Depósito y Vendedor para Frontend Mobile

## Estado

Aceptado

## Contexto

Para la incorporación de la aplicación móvil destinada a la operatoria ágil en sucursales y depósitos (escaneo de códigos de barra, conteo in-situ, consulta de stock consolidado y transferencias), se identificó la necesidad de simplificar la experiencia de usuario (UX) para los empleados de salón y depósito:
1. En el día a día operativo de los puntos de venta, los colaboradores alternan funciones de atención al cliente y logística interna, por lo que requerir perfiles separados provocaría fricción innecesaria (cierres y aperturas constantes de sesión).
2. Sin embargo, en el backend y en la base de datos relacional (MySQL) ya existen roles diferenciados (`ADMINISTRADOR`, `VENTAS`, `DEPOSITO`), y a futuro se prevé incorporar una segregación más estricta a medida que la organización escale (conforme a los requerimientos de la Issue #260).
3. Modificar la base de datos para fusionar físicamente los roles en un único registro `EMPLEADO` causaría pérdida irreversible de granularidad histórica y exigiría costosas migraciones y re-clasificaciones manuales cuando se active la segregación fina.

## Decisión

1. **Preservación de la Segregación en Base de Datos y Backend**:
   Se mantienen intactos los roles granulares en la base de datos (`ADMINISTRADOR`, `VENTAS`, `DEPOSITO`). No se eliminan registros de la tabla `roles` ni se alteran modelos o esquemas en MySQL.

2. **Abstracción Lógica en API (`es_empleado`)**:
   El backend provee un contrato desacoplado exponiendo la bandera booleana `es_empleado` tanto en `/api/usuarios/login/` como en `/api/usuarios/me/`, calculada dinámicamente mediante la propiedad:
   ```python
   @property
   def es_empleado(self):
       return self.rol is not None and self.rol.nombre.lower() in [
           "empleado",
           "ventas",
           "deposito",
       ]
   ```
   A su vez, el payload de usuario continúa incluyendo el detalle formal del rol (`rol: {"id": ..., "nombre": "..."}`).

3. **Consumo Simplificado en la Aplicación Mobile**:
   La aplicación móvil implementa su matriz de interfaz y navegación basándose inicialmente en el flag consolidado `es_empleado`. Cualquier operador con rol `VENTAS` o `DEPOSITO` accede al conjunto unificado de herramientas operativas (búsqueda de catálogo, escáner, control de existencias y registro de traslados/salidas).

4. **Preparación Transparente para Segregación Futura**:
   Cuando en fases posteriores se decida activar la segregación estricta de permisos en mobile (ej. restringir altas de mercadería exclusivamente al personal de depósito), la aplicación móvil podrá comenzar a evaluar el objeto `user.rol.nombre` directamente, sin requerir ningún cambio de esquema en la base de datos ni reprocesamiento de usuarios existentes.

## Consecuencias

### Positivas (+)
- **Cero Impacto en Base de Datos:** No requiere migraciones (`makemigrations`), scripts SQL destructivos ni alteración de claves foráneas.
- **UX Móvil Fluida:** El personal operativo utiliza una única sesión unificada para todas las tareas de campo.
- **Evolución sin Deuda Técnica:** La información granular nunca se pierde en el backend, permitiendo encender controles restrictivos en futuras versiones con mínimo esfuerzo.

### Negativas / Trade-offs (-)
- Durante la etapa inicial, la app móvil no restringe internamente qué operador realiza tareas de salón vs tareas de depósito (riesgo asumido y deseado para maximizar agilidad operativa inicial).

## Implementación / Notas

- **Archivos de Referencia:**
  - Backend: `Backend/usuarios/models.py`, `Backend/usuarios/views.py`.
  - Documentación: `Docs/API_MOBILE.md`.
  - Backlog: Preserva la base estructural para la evolución de la Issue #260.
