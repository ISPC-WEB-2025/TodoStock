# CodeLab_Stock: sistema de gestión de stock

[![Frontend en Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=flat&logo=vercel)](https://todo-stock.vercel.app/)
[![Backend en Alwaysdata](https://img.shields.io/badge/Backend-Alwaysdata-blue?style=flat)](https://todostock.alwaysdata.net/api/)
![Static Badge](https://img.shields.io/github/last-commit/ISPC-WEB-2025/CodeLab?label=Último%20cambio&color=blue)

## 1. Descripción del proyecto

Este proyecto consiste en el desarrollo de una **plataforma web integral** diseñada para la administración y control de inventarios en tiempo real. La idea es que el sistema permita a las empresas gestionar sus productos, proveedores y movimientos de mercadería de manera ágil y centralizada.

Muchas pequeñas y medianas empresas aún dependen de procesos manuales o planillas de cálculo propensas a errores para controlar sus activos. Esto deriva en diversos problemas como:

- _Falta de visibilidad_, es decir, no saber con certeza cuánta mercadería hay disponible.

- _Pérdida de ventas_, debido a la ausencia de alertas tempranas en las bajas de stock.

- _Desperdicio de capital_ por exceso de productos estacionales o de baja rotación acumulados en depósito.

- _Desorganización_ y dificultad para rastrear entradas y salidas de distintas sucursales o depósitos.

Nuestra solución se diferencia por las siguientes características:

- **Modular y adaptable**: su estructura permite configurar categorías y atributos de productos según el rubro de la empresa (desde una ferretería hasta una tienda de ropa).

- **Escalable**: gracias al uso de una API REST sólida, el sistema puede crecer en funciones sin comprometer el rendimiento.

- **Accesibilidad total**: al ser una aplicación web, los dueños de negocio pueden monitorear su stock desde cualquier dispositivo con acceso a internet.

- **Interfaz intuitiva**: diseñada con foco en la experiencia de usuario (UX) para reducir la curva de aprendizaje del personal.

## 2. Instrucciones de instalación

### Prerrequisitos

Antes de comenzar, asegurate de tener instalado:

- **Git** → [git-scm.com](https://git-scm.com)
- **Node.js** (v18 o superior, incluye npm) → [nodejs.org](https://nodejs.org)
- **Python** (v3.10 o superior) → [python.org](https://python.org)
- **MySQL** → [mysql.com](https://mysql.com)

---

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>
```

---

### 2. Frontend (Angular)

**a.** Instalar Angular CLI globalmente (si no está instalado):

```bash
npm install -g @angular/cli
```

**b.** Verificar la instalación:

```bash
ng version
```

**c.** _(Solo Windows)_ Permitir ejecución de scripts en PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**d.** Navegar a la carpeta del proyecto frontend:

```bash
cd Frontend/app-stock
```

**e.** Instalar dependencias:

```bash
npm install
```

**f.** Iniciar el servidor de desarrollo:

```bash
ng serve
```

> [!NOTE]
> Al ejecutar `npm install` pueden aparecer advertencias de dependencias deprecadas. Estas corresponden a dependencias internas de Angular v19 y no afectan el funcionamiento de la aplicación. **No ejecutar** `npm audit fix --force` ya que puede romper la compatibilidad del proyecto.

---

### 3. Backend (Django)

**a.** Crear y activar el entorno virtual:

```bash
# Crear
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

**b.** Instalar dependencias:

```bash
pip install -r requirements.txt
```

**c.** Crear la base de datos en MySQL:

```sql
CREATE DATABASE nombre_db;
```

**d.** Crear el archivo de variables de entorno copiando el modelo:

```bash
cp .env_modelo .env
```

**e.** Completar `.env` con tus credenciales de MySQL.

**f.** Inicializar la base de datos:

#### Opción A — Script automatizado (recomendado)

Con el entorno virtual activado, desde la carpeta `Backend/`:

```bash
python setup_db.py
```

Este script realiza de forma integral:

1. Creación de la base de datos MySQL (si no existe).
2. Ejecución de migraciones de Django.
3. Carga automática de los roles base (`roles.json`: `ADMINISTRADOR`, `VENTAS`, `DEPOSITO`).
4. Creación de la estructura de tablas y datos de prueba completos de inventario y stock.
5. Creación automática del usuario superadmin por defecto (`admin@codelab.com` / `AdminPassword123!`).

#### Opción B — Manual

1. Correr `scripts/todostock_db.sql` en SQL Workbench.
2. `python manage.py migrate`
3. `python manage.py loaddata roles.json`
4. Crear usuario administrador con `python scripts/crear_superadmin.py` o `python manage.py createsuperuser`.

---

**g.** Gestión de superusuarios:

El setup automatizado ya deja configurado el superadmin por defecto (`admin@codelab.com` / `AdminPassword123!`). Si deseas crear o resetear un superadmin en cualquier momento, puedes ejecutar:

```bash
python scripts/crear_superadmin.py
```

O crear un usuario personalizado mediante:

```bash
python manage.py createsuperuser
```

> [!NOTE]
> El superusuario permite acceder al panel de administración en `http://127.0.0.1:8000/admin/` o al dashboard del frontend para gestionar productos, stock, traslados y asignar roles a los usuarios registrados (**ADMINISTRADOR**, **VENTAS**, **DEPOSITO**).

---

**h.** Iniciar el servidor de desarrollo:

```bash
python manage.py runserver
```

---

## 3. Despliegue en producción y uso básico

### 🌐 Aplicación en Producción (En vivo)

| Componente                  | Plataforma | URL pública                                                                        |
| :-------------------------- | :--------- | :--------------------------------------------------------------------------------- |
| **Frontend (Web SPA)**      | Vercel     | [https://todo-stock.vercel.app/](https://todo-stock.vercel.app/)                   |
| **Backend (API REST)**      | Alwaysdata | [https://todostock.alwaysdata.net/api/](https://todostock.alwaysdata.net/api/)     |
| **Panel de Administración** | Alwaysdata | [https://todostock.alwaysdata.net/admin/](https://todostock.alwaysdata.net/admin/) |

### 💻 Entorno de Desarrollo Local y Credenciales Demo

Si ejecutas el proyecto de manera local en tu máquina siguiendo los pasos de instalación anteriores, la base de datos se poblará automáticamente con la siguiente cuenta de administrador de prueba:

- **Email:** `admin@codelab.com`
- **Contraseña:** `AdminPassword123!`
- **Rol:** `ADMINISTRADOR` (Acceso completo a Dashboard, Gestión de Productos, Proveedores, Sucursales, Usuarios y Configuración de Stock).

Las rutas locales operarán en:

- Backend corre en <http://127.0.0.1:8000/>
- API de inventario en <http://127.0.0.1:8000/api/inventario/>
- API de vendedor en <http://127.0.0.1:8000/api/vendedor/>
- API de usuarios en <http://127.0.0.1:8000/api/usuarios/>
- Panel de administración en <http://127.0.0.1:8000/admin/>
- Frontend corre en <http://localhost:4200/>

## 4. Lista de requerimientos

- **Requerimientos Funcionales (RF)**

| ID      | Descripción                                                                                                                                                                      | Prioridad | Actor                    |
| :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------: | :----------------------- |
| **RF1** | **Registro de productos:** El sistema debe permitir dar de alta productos ingresando: nombre, descripción, precio, código y stock inicial.                                       |   Must    | Administrador            |
| **RF2** | **Gestión de productos:** El sistema debe permitir crear, editar y eliminar productos del catálogo.                                                                              |   Must    | Administrador / Vendedor |
| **RF3** | **Gestión de proveedores:** El sistema debe permitir registrar, editar y eliminar proveedores, asociándolos a los productos correspondientes.                                    |   Must    | Administrador            |
| **RF4** | **Registro de movimientos:** El sistema debe registrar cada entrada y salida de mercadería, indicando fecha, cantidad, producto y usuario responsable.                           |   Must    | Vendedor                 |
| **RF5** | **Gestión de inventario:** El sistema debe permitir actualizar el stock de un producto existente, registrando tanto entradas como salidas de mercadería.                         |   Must    | Vendedor                 |
| **RF6** | **Baja de productos:** El sistema debe permitir eliminar un producto del catálogo.                                                                                               |   Must    | Administrador            |
| **RF7** | **Alertas de stock mínimo:** El sistema debe notificar al usuario cuando el stock de un producto caiga por debajo de un umbral mínimo configurable.                              |  Should   | Sistema                  |
| **RF8** | **Autenticación de usuarios:** El sistema debe contar con un módulo de inicio de sesión que permitirá el acceso únicamente a usuarios registrados mediante usuario y contraseña. |   Must    | Administrador            |

- **Requerimientos No Funcionales (RNF)**

| ID       | Categoría         | Descripción                                                                                                                                                                                                                                                     |
| :------- | :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RNF1** | **Seguridad**     | El sistema no debe exponer credenciales de base de datos, tokens de API ni datos de usuarios en respuestas, logs públicos o código del cliente.                                                                                                                 |
| **RNF2** | **Rendimiento**   | Los datos modificados en el inventario deben ser visibles para todos los usuarios en un tiempo de respuesta menor a 2 segundos, medido bajo condiciones normales de operación con hasta 50 usuarios concurrentes y carga de red estable.                        |
| **RNF3** | **Usabilidad**    | La interfaz debe adaptarse correctamente a dispositivos móviles, tablets y escritorio, garantizando que todos los elementos sean legibles e interactuables sin desplazamiento horizontal. Compatible con Chrome ≥ 110, Firefox ≥ 110, Safari ≥ 16 y Edge ≥ 110. |
| **RNF4** | **Accesibilidad** | La plataforma debe ser accesible para usuarios con discapacidades visuales, motoras o cognitivas.                                                                                                                                                               |

## 5. Tecnologías y arquitectura

- **Frontend:** Angular 21 (Standalone components, TypeScript, RxJS, Bootstrap 5) — _Alojado en Vercel_
- **Backend:** Python 3.10+, Django 6.0 y Django Rest Framework 3.17 — _Alojado en Alwaysdata_
- **Base de Datos:** MySQL — _Alojada en Alwaysdata_
- **Estilos:** CSS3 y Bootstrap (modales y notificaciones toast)
