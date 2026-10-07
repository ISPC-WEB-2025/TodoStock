# Product Backlog Completo - TodoStock App Móvil

> **Proyecto:** TodoStock - ISPC 2026  
> **Sprint:** Sprint 2  
> **Repositorio:** [ISPC-WEB-2025/TodoStock-AppMovil](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil)  
> **Estado:** Documento consolidado con la información completa e íntegra de GitHub Issues  

---

## 1. Índice Resumen de Issues y Historias de Usuario

| Código / Tipo | Issue GitHub | Título / Alcance | Asignado(s) | Estado |
| :--- | :---: | :--- | :--- | :---: |
| [Detalle Issue #55](#issue-55) | [#55](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/55) | #US01 Como usuario quiero iniciar sesión y acceder a un menú principal para navegar hacia el resto de la app según mi rol. | mikefink22 | OPEN |
| [Detalle Issue #56](#issue-56) | [#56](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/56) | #US02 Como usuario quiero elegir la sucursal con la que voy a trabajar para que las demás pantallas muestren su información. | candebar | OPEN |
| [Detalle Issue #57](#issue-57) | [#57](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/57) | #US03 Como Administrador o Empleado quiero ver una lista de productos con su cantidad de stock de la sucursal elegida para conocer la situación del inventario. | virginia-garcia | OPEN |
| [Detalle Issue #58](#issue-58) | [#58](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/58) | #US04 Como usuario quiero ver una pantalla de contacto para comunicarme con soporte si lo necesito. | PedroGonzalez1212 | OPEN |
| [Detalle Issue #59](#issue-59) | [#59](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/59) | #US05 Como Administrador quiero cargar un nuevo producto para que esté disponible en el catálogo. | PedroGonzalez1212 | OPEN |
| [Detalle Issue #60](#issue-60) | [#60](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/60) | #US06 Como Empleado o Administrador quiero registrar un movimiento de stock entre dos sucursales para que la existencia se actualice en ambas. | AylenBL8 | OPEN |
| [Detalle Issue #61](#issue-61) | [#61](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/61) | #US07 Como visitante quiero registrarme con mis datos para solicitar mi cuenta en la app. | AylenBL8 | OPEN |
| [Detalle Issue #62](#issue-62) | [#62](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/62) | #US08 Como Administrador quiero cargar, aprobar, listar, editar y dar de baja usuarios para controlar quién accede y con qué rol. | PedroGonzalez1212 | OPEN |
| [Detalle Issue #63](#issue-63) | [#63](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/63) | #US09 Como Administrador quiero editar y eliminar productos para mantener el catálogo libre de datos obsoletos. | virginia-garcia | OPEN |
| [Detalle Issue #64](#issue-64) | [#64](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/64) | #US10 Como usuario quiero ver una pantalla de ayuda con una imagen o un video para aprender a usar la app. | AylenBL8 | OPEN |
| [Detalle Issue #65](#issue-65) | [#65](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/65) | [RNF-UX] Diseño adaptable y persistencia de estado ante rotación | mikefink22 | OPEN |
| [Detalle Issue #66](#issue-66) | [#66](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/66) | [RELEASE] Empaquetado APK, despliegue y video demo del Sprint 2 | candebar | OPEN |
| [Detalle Issue #67](#issue-67) | [#67](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/67) | #US11 Como usuario quiero conocer y controlar el uso de mis datos personales para ejercer mis derechos. | AylenBL8 | OPEN |
| [Detalle Issue #68](#issue-68) | [#68](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/68) | [RNF-SEG] Hardening de seguridad, protección de sesiones y datos sensibles | PedroGonzalez1212 | OPEN |
| [Detalle Issue #69](#issue-69) | [#69](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/69) | [ENABLER-QA] Suite de pruebas automatizadas, pipeline CI/CD e informe de accesibilidad | mikefink22 | OPEN |
| [Detalle Issue #70](#issue-70) | [#70](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/70) | #US12 Como usuario (Administrador o Empleado) quiero ver y editar mis datos personales para mantener mi información actualizada. | candebar | OPEN |
| [Detalle Issue #71](#issue-71) | [#71](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/71) | [MGMT] Documentación del Sprint 2, registro de ceremonias y actualización de Wiki | OctavioArnaudo | OPEN |

---

## 2. Detalle Completo de Cada Issue (Criterios de Aceptación y Tareas Técnicas)

<a id="issue-55"></a>
### Issue #55: #US01 Como usuario quiero iniciar sesión y acceder a un menú principal para navegar hacia el resto de la app según mi rol.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/55](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/55)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Miguel Flores (@mikefink22)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Existe una pantalla de Login con usuario y contraseña, y un Menú Principal accesible después de iniciar sesión.
- [ ] El Menú Principal muestra solo las opciones del rol: el Administrador ve Usuarios, Productos, Sucursal, Stock y Movimientos; el Empleado ve Sucursal, Stock y Movimientos. Ambos ven Contacto, Ayuda, Darme de baja y Cerrar sesión.
- [ ] Las credenciales se validan contra la API y solo un usuario aprobado accede al menú; el rol queda disponible para las demás pantallas.
- [ ] Un usuario registrado que todavía no fue aprobado por un Administrador no puede ingresar y ve un mensaje claro.
- [ ] Existe una forma de cerrar sesión que vuelve a Login y borra el token guardado.
- [ ] Los mensajes de error del Login se ven sin superponerse con otros elementos.

## Tareas
- TK90 Configuración base de la app para consumir la API (Aylen, 2 SP)
- TK05 Retrofit: login contra la API y guardado del JWT (Miguel, 2 SP)
- TK06 Interceptor HTTP Authorization: Bearer <token> (Miguel, 1 SP)
- TK07 Botón Cerrar sesión (Miguel, 1 SP)
- TK91 SplashActivity: decidir el destino según la sesión guardada (Miguel, 1 SP)
- TK92 Corregir defecto visual de errores en Login (TC-L-01) (Miguel, 1 SP)


---

<a id="issue-56"></a>
### Issue #56: #US02 Como usuario quiero elegir la sucursal con la que voy a trabajar para que las demás pantallas muestren su información.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/56](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/56)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Candelaria Barjollo (@candebar)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Se muestra la lista de sucursales real (desde la API).
- [ ] Al seleccionar una sucursal, su identificador viaja por Intent hacia las pantallas que lo necesitan.
- [ ] La pantalla es accesible desde el Menú Principal y se puede volver atrás.

## Tareas
- TK12 Sucursales desde la API (Candelaria, 2 SP)


---

<a id="issue-57"></a>
### Issue #57: #US03 Como Administrador o Empleado quiero ver una lista de productos con su cantidad de stock de la sucursal elegida para conocer la situación del inventario.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/57](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/57)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Virginia Garcia (@virginia-garcia)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] La pantalla recibe la sucursal elegida en US02 y muestra productos con su cantidad real.
- [ ] Los productos bajo el umbral mínimo se destacan visualmente.
- [ ] La pantalla es accesible para ambos roles.

## Tareas
- TK16 Stock real por sucursal (Virginia, 3 SP)
- TK17 Alerta visual de stock bajo el umbral mínimo (Virginia, 2 SP)


---

<a id="issue-58"></a>
### Issue #58: #US04 Como usuario quiero ver una pantalla de contacto para comunicarme con soporte si lo necesito.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/58](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/58)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** pedro gonzalez (@PedroGonzalez1212)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] La pantalla es accesible desde el Menú Principal (el menú de opciones posterior al inicio de sesión) para ambos roles.
- [ ] El formulario confirma el envío solo si fue exitoso.
- [ ] Es una pantalla obligatoria según la consigna.

## Tareas
- TK20 Selector de sucursal del formulario de contacto con datos reales (Pedro, 1 SP)
- TK42 Endpoint de contacto y envío real desde ContactoActivity (Pedro, 2 SP)


---

<a id="issue-59"></a>
### Issue #59: #US05 Como Administrador quiero cargar un nuevo producto para que esté disponible en el catálogo.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/59](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/59)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** pedro gonzalez (@PedroGonzalez1212)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] El formulario permite ingresar nombre, descripción, precio y código.
- [ ] El producto se guarda contra la API.
- [ ] Solo el rol Administrador accede.

## Tareas
- TK23 Alta de producto contra la API (solo Administrador) (Pedro, 2 SP)
- TK93 Corregir defecto visual de errores en Carga de Producto (TC-CP-01) (Pedro, 1 SP)


---

<a id="issue-60"></a>
### Issue #60: #US06 Como Empleado o Administrador quiero registrar un movimiento de stock entre dos sucursales para que la existencia se actualice en ambas.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/60](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/60)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Aylén Bartolino Luna (@AylenBL8)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] El formulario permite elegir origen, destino, producto y cantidad reales.
- [ ] El movimiento se registra de forma atómica.
- [ ] No se puede confirmar con origen y destino iguales ni con cantidad menor o igual a cero.

## Tareas
- TK27 Movimiento atómico real entre sucursales (Aylen, 3 SP)


---

<a id="issue-61"></a>
### Issue #61: #US07 Como visitante quiero registrarme con mis datos para solicitar mi cuenta en la app.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/61](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/61)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Aylén Bartolino Luna (@AylenBL8)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Con nombre, email, contraseña y confirmación válidos y los términos aceptados, se crea la cuenta en estado pendiente y se vuelve a Login con un mensaje que avisa que un Administrador debe aprobarla.
- [ ] La cuenta pendiente no tiene rol y no puede iniciar sesión hasta que un Administrador la acepte y le asigne un rol.
- [ ] Con un email que ya existe, se muestra un error claro y no se duplica el usuario.
- [ ] Con una contraseña débil se rechaza indicando qué falta, en la app y en el servidor.
- [ ] Los términos y condiciones se pueden leer desde la pantalla de Registro; si no se marcan, el botón Registrarme no envía nada.

## Tareas
- TK35 Endpoint de registro con estado pendiente y migración de consentimiento (Aylen, 3 SP)
- TK47 Política de contraseñas robustas (servidor y app) (Aylen, 2 SP)
- TK34 RegistroActivity: layout, validaciones y conexión a la API (Aylen, 4 SP)


---

<a id="issue-62"></a>
### Issue #62: #US08 Como Administrador quiero cargar, aprobar, listar, editar y dar de baja usuarios para controlar quién accede y con qué rol.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/62](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/62)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** pedro gonzalez (@PedroGonzalez1212)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Un Administrador logueado ve la lista con nombre, email y rol.
- [ ] El Administrador ve los usuarios registrados pendientes y puede aceptarlos asignándoles un rol, o rechazarlos.
- [ ] El Administrador puede cargar un usuario nuevo desde un formulario, con su rol.
- [ ] Al cambiar el rol o los datos y guardar, el cambio persiste y se refleja en la lista.
- [ ] Al dar de baja y confirmar, el usuario deja de aparecer y no puede iniciar sesión; si se cancela, no cambia nada.
- [ ] Un Empleado no ve la pantalla y la API responde 403.

## Tareas
- TK36 API de usuarios (listar, editar, baja) solo Administrador (Pedro, 3 SP)
- TK37 Gestión de usuarios: lista, edición y baja con diálogo (Pedro, 3 SP)
- TK109 Cargar usuario y aprobar registros pendientes (Administrador) (Miguel, 3 SP)


---

<a id="issue-63"></a>
### Issue #63: #US09 Como Administrador quiero editar y eliminar productos para mantener el catálogo libre de datos obsoletos.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/63](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/63)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Virginia Garcia (@virginia-garcia)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Se pueden modificar nombre, descripción, precio o código y se guardan contra la API.
- [ ] Al eliminar y confirmar, el producto deja de aparecer y no se puede elegir en nuevos movimientos.
- [ ] Un código que ya pertenece a otro producto muestra el error y no lo pisa.

## Tareas
- TK38 API de productos: edición y baja lógica (Virginia, 2 SP)
- TK39 Listado de productos con editar y eliminar (Virginia, 3 SP)


---

<a id="issue-64"></a>
### Issue #64: #US10 Como usuario quiero ver una pantalla de ayuda con una imagen o un video para aprender a usar la app.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/64](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/64)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Aylén Bartolino Luna (@AylenBL8)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Desde el Menú Principal se abre una Activity nueva (Ayuda) con el recurso multimedia.
- [ ] Los controles del video y la imagen tienen descripción para TalkBack.
- [ ] Al rotar el dispositivo, la Activity no se cierra ni pierde la posición del video.

## Tareas
- TK40 Activity multimedia de Ayuda con imagen y/o video (Aylen, 2 SP)


---

<a id="issue-65"></a>
### Issue #65: [RNF-UX] Diseño adaptable y persistencia de estado ante rotación

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/65](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/65)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Miguel Flores (@mikefink22)
- **Etiquetas:** `ui-ux`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Al rotar el dispositivo no hay textos cortados ni superpuestos y no se pierde lo cargado en el formulario.
- [ ] La app instala y se ve bien en pantalla chica y tableta con el minSdk definido.
- [ ] El diagrama de navegabilidad está publicado en la Wiki y coincide con lo que hace la app (TK102, en US17).

## Tareas
- TK41 Layouts landscape y tablet, y estado al rotar (Miguel, 3 SP)


---

<a id="issue-66"></a>
### Issue #66: [RELEASE] Empaquetado APK, despliegue y video demo del Sprint 2

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/66](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/66)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Candelaria Barjollo (@candebar)
- **Etiquetas:** `gestion`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Con el backend desplegado, la app se conecta por HTTPS a la URL del ambiente sin cambiar código.
- [ ] El release en main incluye el APK o zip y un README con pasos de instalación y usuarios de prueba que no son credenciales reales.
- [ ] Hay un video demo grupal de 3 minutos o menos con todo el equipo.

## Tareas
- TK43 Deploy del backend y baseUrl de release (Candelaria, 3 SP)
- TK44 APK o zip, release en main y pasos de instalación (Candelaria, 2 SP)
- TK97 Grabar y editar el video demo grupal (máx. 3 minutos) (Virginia, 2 SP)


---

<a id="issue-67"></a>
### Issue #67: #US11 Como usuario quiero conocer y controlar el uso de mis datos personales para ejercer mis derechos.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/67](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/67)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Aylén Bartolino Luna (@AylenBL8)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Desde el Registro puedo leer los términos y la política de privacidad antes de aceptarlos.
- [ ] Al aceptar los términos, el sistema guarda fecha y versión junto a mi usuario.
- [ ] El Menú Principal tiene la opción 'Darme de baja': al confirmar, la cuenta se desactiva, mis datos personales se eliminan o anonimizan y queda registro en la auditoría.

## Tareas
- TK52 Legislación en la app: términos, aceptación y 'Darme de baja' (Aylen, 3 SP)


---

<a id="issue-68"></a>
### Issue #68: [RNF-SEG] Hardening de seguridad, protección de sesiones y datos sensibles

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/68](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/68)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** pedro gonzalez (@PedroGonzalez1212)
- **Etiquetas:** `ciberseguridad`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] El repositorio no contiene credenciales ni claves reales (ni en crear_superadmin.py ni en el README).
- [ ] Un origen no autorizado o un host no listado es rechazado.
- [ ] Superado el límite de intentos de login, este se bloquea temporalmente.
- [ ] Un endpoint protegido llamado sin token o con un rol sin permiso responde 401 o 403.
- [ ] Login, altas, bajas y movimientos quedan en una tabla de auditoría.
- [ ] Existe el Sistema de Gestión de Riesgos y el video de autenticación y autorización.

## Tareas
- TK45 Sacar credenciales del script y del README; secretos a .env (Pedro, 3 SP)
- TK46 CORS, ALLOWED_HOSTS y límite de intentos de login (Pedro, 3 SP)
- TK48 Autorización por perfiles (Administrador / Empleado) y menú por rol (Miguel, 3 SP)
- TK49 Control de sesiones: access corto, refresh con rotación y cierre por inactividad (Virginia, 2 SP)
- TK50 TLS: certificado, redirección a HTTPS, HSTS y network_security_config (Candelaria, 2 SP)
- TK51 Auditoría: tabla LogAuditoria (Virginia, 3 SP)
- TK53 Sistema de Gestión de Riesgos y revisión del plan de seguridad (Candelaria, 4 SP)
- TK54 Video corto: por qué JWT, autenticación y autorización (Miguel, 2 SP)
- TK55 TC-SEG-01: caso de prueba de seguridad (autenticación y sesiones) (Miguel, 1 SP)
- TK56 TC-SEG-02: caso de prueba de seguridad (contraseñas robustas) (Candelaria, 1 SP)
- TK57 TC-SEG-03: caso de prueba de seguridad (autorización por rol) (Virginia, 1 SP)
- TK58 TC-SEG-04: caso de prueba de seguridad (fuerza bruta) (Pedro, 1 SP)
- TK59 TC-SEG-05: caso de prueba de seguridad (legislación y auditoría) (Aylen, 1 SP)


---

<a id="issue-69"></a>
### Issue #69: [ENABLER-QA] Suite de pruebas automatizadas, pipeline CI/CD e informe de accesibilidad

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/69](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/69)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Miguel Flores (@mikefink22)
- **Etiquetas:** `testing`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Cuando corre el pipeline, ejecuta los tests unitarios y de red y queda en verde.
- [ ] Cada test automatizado se rastrea a un caso de prueba y a una historia en la Matriz de Trazabilidad.
- [ ] Cada integrante es autor de al menos un test automatizado y de un hallazgo de accesibilidad reportado como Issue.

## Tareas
- TK60 [AUT-UNIT-01] Tests unitarios de validadores (Aylen, 2 SP)
- TK61 [AUT-UNIT-02] Tests unitarios de stock bajo umbral y mappers (Virginia, 2 SP)
- TK62 [AUT-UNIT-03] Tests unitarios de repositorios (Pedro, 2 SP)
- TK63 [AUT-UNIT-04] Tests unitarios de token, sesión y AuthInterceptor (Miguel, 2 SP)
- TK64 [AUT-NET-01] Integración de red: parseo de respuestas correctas (Candelaria, 2 SP)
- TK65 [AUT-NET-02] Integración de red: errores HTTP (Candelaria, 2 SP)
- TK66 [AUT-NET-03] Integración de red: timeout y falta de conexión (Candelaria, 1 SP)
- TK67 [AUT-API-01] Colección Postman de autenticación (Virginia, 2 SP)
- TK68 [AUT-API-02] Colección Postman de productos (Miguel, 3 SP)
- TK69 [AUT-API-03] Colección Postman de sucursales, stock, movimientos y contacto (Pedro, 2 SP)
- TK70 [AUT-UI-01] Espresso: flujo Login → Menú con LoginScreen (Miguel, 2 SP)
- TK71 [AUT-UI-02] Espresso: alta de producto como Administrador (Pedro, 2 SP)
- TK72 [AUT-UI-03] Espresso: movimiento con las validaciones de TK26 (Aylen, 2 SP)
- TK73 [AUT-SYS-01] UI Automator: flujo con permiso, o justificación escrita (Aylen, 1 SP)
- TK74 [AUT-E2E-01] Appium: flujo smoke sobre el APK instalado (deseable) (Virginia, 3 SP)
- TK75 [ACC-01] Auditoría con Accessibility Scanner (Candelaria, 2 SP)
- TK76 [ACC-02] AccessibilityChecks.enable() en los tests Espresso (Miguel, 2 SP)
- TK77 [ACC-03] TalkBack: un flujo crítico completo (Virginia, 2 SP)
- TK78 [ACC-04] Etiquetas y áreas táctiles de 48 × 48 dp (Pedro, 2 SP)
- TK79 [ACC-05] Contraste, tamaño de texto y errores anunciados (Aylen, 2 SP)
- TK80 Plan de Pruebas (Miguel, 3 SP)
- TK81 Pipeline de GitHub Actions con JaCoCo y Newman (Candelaria, 3 SP)
- TK82 Planilla de Test Cases con columnas nuevas y trazabilidad a la historia (Virginia, 2 SP)
- TK83 Matriz de Trazabilidad de Requisitos (Pedro, 2 SP)
- TK84 Página Testing.md de la Wiki (Aylen, 2 SP)
- TK85 Ejecución de casos: TC-L-03, TC-L-04, TC-SSUC-01 y TC-STK-01 (Miguel, 2 SP)
- TK86 Ejecución de casos: TC-MOV-001, TC-MOV-006, TC-REG-03 y TC-REG-04 (Candelaria, 2 SP)
- TK87 Ejecución de casos: TC-SSUC-02, TC-MOV-002, TC-MOV-003 y TC-REG-01 (Virginia, 2 SP)
- TK88 Ejecución de casos: TC-STK-02, TC-MOV-004, TC-MOV-005 y TC-REG-02 (Pedro, 2 SP)
- TK89 Ejecución de casos: TC-L-01, TC-L-02, TC-CP-01 y TC-C-01 (Aylen, 2 SP)
- TK96 Informe de Accesibilidad (Pedro, 2 SP)


---

<a id="issue-70"></a>
### Issue #70: #US12 Como usuario (Administrador o Empleado) quiero ver y editar mis datos personales para mantener mi información actualizada.

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/70](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/70)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):** Candelaria Barjollo (@candebar)
- **Etiquetas:** `historia de usuario`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] Desde el Menú Principal se abre la pantalla de perfil sin cerrar la app.
- [ ] Muestra mis datos y me permite editarlos y guardarlos contra la API.
- [ ] Un usuario solo puede ver y editar su propio perfil.

## Tareas
- TK94 API del perfil propio (Candelaria, 2 SP)
- TK95 PerfilActivity: ver y editar mis datos (Candelaria, 3 SP)


---

<a id="issue-71"></a>
### Issue #71: [MGMT] Documentación del Sprint 2, registro de ceremonias y actualización de Wiki

- **Link oficial:** [https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/71](https://github.com/ISPC-WEB-2025/TodoStock-AppMovil/issues/71)
- **Estado:** `OPEN` | **Milestone:** `Sprint 2`
- **Responsable(s):**  (@OctavioArnaudo)
- **Etiquetas:** `gestion, documentacion`

#### Contenido, Criterios y Tareas:

## Criterios de aceptación
- [ ] El Milestone Sprint 2 tiene todos los Issues con sus criterios de aceptación y el Kanban tiene las 5 columnas actualizadas.
- [ ] La Wiki tiene las 4 ceremonias del sprint, los avances individuales y de equipo, y los enlaces a aplicaciones externas.
- [ ] El IEEE830 y su Anexo II están actualizados y el diagrama de navegabilidad está publicado.
- [ ] El Product Backlog de la Wiki coincide con este backlog.
- [ ] Están publicados los términos, la política de privacidad y la sección legal.
- [ ] El README está completo y sin credenciales.

## Tareas
- TK98 Milestone Sprint 2, etiquetas e Issues en GitHub (Aylen, 2 SP)
- TK99 Tablero Kanban con las 5 columnas y gestión de bugs (Octavio, 1 SP)
- TK100 Registro de las 4 ceremonias del Sprint 2 en la Wiki (Octavio, 3 SP)
- TK101 IEEE830 actualizado con los requerimientos del Sprint 2 (Octavio, 2 SP)
- TK102 Diagrama de navegabilidad y Anexo II con capturas de las pantallas nuevas (Octavio, 2 SP)
- TK103 Wiki: avances individuales, de equipo y enlaces a aplicaciones externas (Octavio, 2 SP)
- TK104 Product Backlog de la Wiki alineado con este backlog (Octavio, 1 SP)
- TK105 Legislación: términos y condiciones, política de privacidad y sección de la Wiki (Octavio, 2 SP)
- TK106 README del repositorio actualizado (Octavio, 2 SP)
- TK107 Guion y coordinación del video demo grupal (Octavio, 1 SP)
- TK108 Commit en main con el backlog y las plantillas de Issues y PR (Octavio, 1 SP)


---
