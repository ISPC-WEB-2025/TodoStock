# Guía Operativa: Despliegue de Backend Django en Alwaysdata

Esta guía detalla el procedimiento paso a paso para desplegar la API REST de **CodeLab Stock** (Django 6.0 + DRF + MySQL) en la plataforma **Alwaysdata** bajo su plan gratuito permanente (*Free Plan* con 1 GB de almacenamiento, MySQL/MariaDB nativo, phpMyAdmin y certificado HTTPS automático).

---

## 📋 Requisitos Previos

1. Cuenta registrada en [Alwaysdata](https://www.alwaysdata.com/) (100% gratuita, solo con email, **sin tarjeta de crédito**).
2. Tu nombre de cuenta / usuario de Alwaysdata (en esta guía representado como `<tu_usuario>`).
3. Acceso al repositorio del proyecto en GitHub: `https://github.com/ISPC-WEB-2025/CodeLab.git`.

---

## 🗄️ Paso 1: Crear la Base de Datos MySQL en Alwaysdata

Alwaysdata incluye un servidor MySQL / MariaDB nativo con panel visual **phpMyAdmin**:

1. En el menú lateral izquierdo de Alwaysdata, hacé clic en **Databases** ➔ **MySQL**.
2. Hacé clic en el botón **"Add a database"** (arriba a la derecha).
3. Asignale el nombre: `todostock_db` (el nombre final será `<tu_usuario>_todostock_db`).
4. En la pestaña **Users** dentro de MySQL:
   * Hacé clic en **"Add a user"**.
   * Nombre de usuario: `<tu_usuario>_admin` (o el nombre que elijas).
   * Contraseña: definí una contraseña segura y guardala.
   * En **Permissions**, asegurate de marcar todos los permisos (GRANT ALL) sobre la base `<tu_usuario>_todostock_db`.
5. Tomá nota de los datos de conexión:
   * **Host:** `mysql-<tu_usuario>.alwaysdata.net`
   * **Base de datos:** `<tu_usuario>_todostock_db`
   * **Usuario:** `<tu_usuario>_admin`
   * **Puerto:** `3306`

> **Tip:** Podés hacer clic en el botón **phpMyAdmin** dentro de Alwaysdata para ingresar a la interfaz gráfica y visualizar tus tablas en cualquier momento.

---

## 💻 Paso 2: Clonar el Repositorio desde la Terminal SSH / Web

Alwaysdata incluye una terminal web directa en el navegador:

1. En el menú lateral, andá a **Remote access** ➔ **SSH**.
2. Asegurate de que el acceso SSH esté habilitado y definí una contraseña para tu usuario SSH si aún no la tenés.
3. Hacé clic en **"Web SSH"** (o conectate desde tu propia terminal con `ssh <tu_usuario>@ssh-<tu_usuario>.alwaysdata.net`).
4. En la terminal remota, cloná el repositorio:
   ```bash
   git clone https://github.com/ISPC-WEB-2025/CodeLab.git
   cd CodeLab/Backend
   ```

---

## 🐍 Paso 3: Crear el Entorno Virtual e Instalar Dependencias

En la terminal dentro de `~/CodeLab/Backend`:

1. Creá el virtualenv con Python:
   ```bash
   python3 -m venv venv
   ```
2. Activá el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
3. Instalá las dependencias del proyecto:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔐 Paso 4: Configurar Variables de Entorno (`.env`)

En `~/CodeLab/Backend`, copiá la plantilla y editá el archivo:

```bash
cp ".env modelo" .env
nano .env
```

Configurá las credenciales con los datos de Alwaysdata:

```env
# Configuración general
SECRET_KEY="tu_clave_secreta_super_larga_y_segura"
DEBUG=False
ALLOWED_HOSTS="<tu_usuario>.alwaysdata.net, localhost"

# Base de datos MySQL en Alwaysdata
DB_NAME="<tu_usuario>_todostock_db"
DB_USER="<tu_usuario>_admin"
DB_PASSWORD="tu_contraseña_definida_en_paso_1"
DB_HOST="mysql-<tu_usuario>.alwaysdata.net"
DB_PORT=3306

# Superadministrador inicial (blindado según Issue #261)
ADMIN_EMAIL="admin@codelab.com"
ADMIN_PASSWORD="TuPasswordSeguro2026!"
```

*(Para guardar y salir en nano: `Ctrl + O`, `Enter`, `Ctrl + X`)*.

---

## ⚡ Paso 5: Inicializar la Base de Datos y Recolectar Estáticos

Con el entorno virtual activo (`source venv/bin/activate`):

1. Ejecutá el script de inicialización:
   ```bash
   python setup_db.py
   ```
   *(Este script creará las tablas, aplicará las migraciones, sembrará los roles y configurará el superadministrador seguro)*.
2. Recolectá los archivos estáticos de Django y DRF:
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## 🌐 Paso 6: Configurar el Sitio Web en Alwaysdata

1. En el menú lateral izquierdo, andá a **Web** ➔ **Sites**.
2. En el sitio por defecto (`<tu_usuario>.alwaysdata.net`), hacé clic en el botón de configuración (ícono de engranaje / editar).
3. Completá los siguientes campos:
   * **Name:** `CodeLab Stock API`
   * **Domain:** `<tu_usuario>.alwaysdata.net`
   * **Type:** Seleccioná **Python WSGI**.
   * **Working directory:**
     ```text
     /home/<tu_usuario>/CodeLab/Backend
     ```
   * **Application path:**
     ```text
     config.wsgi:application
     ```
   * **Python version:** Seleccioná la versión de Python instalada (ej. 3.10 o 3.11).
   * **Virtualenv directory:**
     ```text
     /home/<tu_usuario>/CodeLab/Backend/venv
     ```
4. **Archivos Estáticos:**
   En la sección **Static paths** (abajo en la misma pantalla):
   * Hacé clic en **"Add a static path"**.
   * **URL:** `/static/`
   * **Directory:** `/home/<tu_usuario>/CodeLab/Backend/staticfiles/`
5. Hacé clic en el botón verde **Submit** al final de la página.
6. En la pestaña **SSL** del sitio, confirmá que el certificado Let's Encrypt gratuito esté habilitado con redirección automática a HTTPS.

---

## 🚀 Paso 7: Probar la API en Producción

Abrí tu navegador e ingresá a:
* **Panel Administrativo:** `https://<tu_usuario>.alwaysdata.net/admin/`
* **Login de Usuarios:** `https://<tu_usuario>.alwaysdata.net/api/usuarios/login/`
* **Catálogo de Productos:** `https://<tu_usuario>.alwaysdata.net/api/inventario/productos/`

---

## 🔄 Despliegue Continuo (Actualizaciones)

Para actualizar con nuevos commits:
```bash
cd ~/CodeLab/Backend
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
En Alwaysdata, hacé clic en el botón de **Restart** en el panel de Sitios.
