# Guía Operativa: Migración y Despliegue de Backend Django en Alwaysdata

Esta guía detalla el procedimiento paso a paso para **limpiar instalaciones previas**, migrar y desplegar de forma ultraligera la API REST de **CodeLab Stock** (Django 6.0 + DRF + MySQL) en la plataforma **Alwaysdata** bajo su plan gratuito permanente (*Free Plan* con **100 MB de almacenamiento**, MySQL nativo, phpMyAdmin y HTTPS automático).

> **Control estricto de cuota (100 MB):** El plan gratuito cuenta con un límite estricto de 100 MB de disco. Un entorno Django básico con su historial Git y estáticos ronda los ~75 a 80 MB. Para evitar el bloqueo por *Disk Quota Exceeded*, esta guía aplica **Git Sparse-Checkout** (sin descargar el código de Angular) e instala paquetes con `--no-cache-dir` (evitando almacenar 35 MB de caché en `~/.cache`).

---

## 📋 Requisitos Previos

1. Cuenta registrada en [Alwaysdata](https://www.alwaysdata.com/) (100% gratuita, solo con email, sin tarjeta).
2. Tu nombre de cuenta / usuario de Alwaysdata (en esta guía representado como `<tu_usuario>`).
3. Acceso al repositorio del proyecto en GitHub: `https://github.com/ISPC-WEB-2025/CodeLab.git`.

---

## 🧹 Paso 1: Limpieza Previa Total en el Servidor (Opcional si es reinstalación)

Si ya tenías un despliegue anterior y querés arrancar desde un estado limpio recuperando el 100% del espacio en disco:

### 1.1 Limpiar archivos, entornos y caché anterior
Abrí la consola **Web SSH** en Alwaysdata (**Remote access** ➔ **SSH** ➔ **Web SSH**):
```bash
# Regresar a la raíz del home
cd ~

# Eliminar carpetas anteriores si existían
rm -rf CodeLab
rm -rf todo_stock

# Purgar caché oculta de pip para recuperar hasta 30-40 MB
rm -rf ~/.cache
```

### 1.2 Limpiar la base de datos MySQL existente
1. En el panel de Alwaysdata, andá a **Databases** ➔ **MySQL**.
2. Hacé clic en el botón **phpMyAdmin**.
3. Seleccioná tu base de datos `<tu_usuario>_todostock_db`.
4. Marcá todas las tablas existentes y seleccioná en el menú desplegable inferior **"Vaciar" (TRUNCATE)** o **"Eliminar" (DROP)**.  
*(No elimines la base de datos en sí; solo sus tablas internas para que el script inicializador las recree desde cero).*

---

## 🗄️ Paso 2: Crear la Base de Datos MySQL (Si es la primera vez)

Si es una cuenta nueva sin base de datos creada:

1. En el menú lateral, andá a **Databases** ➔ **MySQL**.
2. Clic en **"Add a database"** ➔ Nombre: `todostock_db` (nombre final: `<tu_usuario>_todostock_db`).
3. En la pestaña **Users** ➔ Clic en **"Add a user"**:
   - Nombre: `<tu_usuario>_admin`.
   - Contraseña: definí una clave segura.
   - En **Permissions**, otorgá permisos completos (**GRANT ALL**) sobre `<tu_usuario>_todostock_db`.
4. Datos de conexión:
   - **Host:** `mysql-<tu_usuario>.alwaysdata.net`
   - **Base de datos:** `<tu_usuario>_todostock_db`
   - **Usuario:** `<tu_usuario>_admin`
   - **Puerto:** `3306`

---

## 📦 Paso 3: Clonado Ultraligero con Historial de Commits Completo

Para mantener **todos los commits históricos** (`git log`, trazabilidad, capacidad de cambio de ramas) pero **sin extraer los pesados archivos de Angular** en disco, usamos Sparse-Checkout:

En la terminal SSH:

```bash
cd ~

# 1. Clonar con TODO el historial de commits, pero sin extraer archivos en disco (--no-checkout)
git clone --branch feature/mobile-backend-readiness-v2 --no-checkout https://github.com/ISPC-WEB-2025/CodeLab.git CodeLab

cd CodeLab

# 2. Configurar Sparse-Checkout para extraer ÚNICAMENTE Backend y Docs
git sparse-checkout init --cone
git sparse-checkout set Backend Docs

# 3. Extraer solo las carpetas elegidas en el árbol de trabajo
git checkout feature/mobile-backend-readiness-v2
```

> **Ventajas:**  
> - En disco solo se extraen `Backend/` y `Docs/` (~35 MB en total).  
> - El cliente web `Frontend/app-stock` nunca se descarga en el servidor.  
> - Podés ejecutar `git log` y ver la totalidad de los commits y ramas del proyecto.

---

## 🐍 Paso 4: Crear el Entorno Virtual e Instalar Dependencias

En la terminal SSH dentro de `~/CodeLab/Backend`:

```bash
cd ~/CodeLab/Backend

# 1. Crear virtualenv con Python 3.10 o 3.11
python3 -m venv venv

# 2. Activar el entorno virtual
source venv/bin/activate

# 3. Instalar dependencias SIN almacenar caché local (vital para no superar los 100 MB)
pip install --no-cache-dir -r requirements.txt
```

---

## 🔐 Paso 5: Configurar Variables de Entorno (`.env`)

En `~/CodeLab/Backend`, creá el archivo `.env` a partir del modelo:

```bash
cp .env.example .env
nano .env
```

Configurá las credenciales con tus valores reales de Alwaysdata:

```env
# Configuración general
SECRET_KEY="tu_clave_secreta_django_super_larga"
DEBUG=False
ALLOWED_HOSTS="<tu_usuario>.alwaysdata.net, localhost, 127.0.0.1"

# Base de datos MySQL en Alwaysdata
DB_NAME="<tu_usuario>_todostock_db"
DB_USER="<tu_usuario>_admin"
DB_PASSWORD="tu_password_definida_en_mysql"
DB_HOST="mysql-<tu_usuario>.alwaysdata.net"
DB_PORT=3306

# Superadministrador inicial (autocreación idempotente)
ADMIN_EMAIL="admin@codelab.com"
ADMIN_PASSWORD="TuPasswordSeguraAdmin2026!"
```

*(Para guardar y salir en nano: `Ctrl + O` ➔ `Enter` ➔ `Ctrl + X`)*.

---

## ⚡ Paso 6: Inicializar la Base de Datos y Recolectar Estáticos

Con el entorno virtual activo (`source venv/bin/activate`):

```bash
# 1. Ejecutar el inicializador automatizado
python setup_db.py

# 2. Recolectar estáticos (WhiteNoise) para el admin de Django y DRF
python manage.py collectstatic --noinput
```

`setup_db.py` realiza automáticamente:
- Ejecución de los scripts de estructura relacional (`01_estructura.sql`, `02_movimiento.sql`, `03_datos.sql`).
- Ejecución de migraciones Django.
- Inicialización de roles (`ADMINISTRADOR`, `EMPLEADO`, `VENTAS`, `DEPOSITO`).
- Creación segura del Superadministrador con las credenciales de tu `.env`.

---

## 🌐 Paso 7: Configurar el Sitio Web en Alwaysdata

1. En el menú lateral izquierdo de Alwaysdata, andá a **Web** ➔ **Sites**.
2. En tu sitio principal (`<tu_usuario>.alwaysdata.net`), hacé clic en el ícono de **Editar** (engranaje).
3. Completá la configuración:
   - **Name:** `CodeLab Stock API`
   - **Domain:** `<tu_usuario>.alwaysdata.net`
   - **Type:** Seleccioná **Python WSGI**.
   - **Working directory:**
     ```text
     /home/<tu_usuario>/CodeLab/Backend
     ```
   - **Application path:**
     ```text
     config.wsgi:application
     ```
   - **Python version:** Seleccioná la misma versión usada para el virtualenv (`3.10` o `3.11`).
   - **Virtualenv directory:**
     ```text
     /home/<tu_usuario>/CodeLab/Backend/venv
     ```
4. **Archivos Estáticos (Static paths):**
   - Hacé clic en **"Add a static path"**.
   - **URL:** `/static/`
   - **Directory:** `/home/<tu_usuario>/CodeLab/Backend/staticfiles/`
5. Hacé clic en **Submit** (botón verde al final).
6. En la pestaña **SSL** del sitio, verificá que el certificado gratuito Let's Encrypt esté habilitado con redirección forzada a HTTPS.
7. Hacé clic en el botón **Restart** del sitio.

---

## 🚀 Paso 8: Verificación y Conexión con la App Móvil

### Comprobación web:
- **Panel Administrativo Django:** `https://<tu_usuario>.alwaysdata.net/admin/`
- **Selector de Roles:** `https://<tu_usuario>.alwaysdata.net/api/usuarios/roles/`
- **Catálogo de Productos:** `https://<tu_usuario>.alwaysdata.net/api/inventario/productos/`

### Configuración en la App Móvil Android (Java 17):
En la clase de configuración de red (Retrofit) de tu proyecto Android, definí la URL base de producción:

```java
public class ApiConstants {
    public static final String BASE_URL = "https://<tu_usuario>.alwaysdata.net/";
}
```

---

## 🔄 Actualizaciones Futuras (Despliegue Continuo)

Cuando se suban nuevos commits al repositorio, actualizar el servidor es tan simple como:

```bash
cd ~/CodeLab/Backend
git pull origin feature/mobile-backend-readiness-v2
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Y finalmente hacés clic en **Restart** en el panel de Sitios de Alwaysdata.
