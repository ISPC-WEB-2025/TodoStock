# Guía Operativa: Despliegue de Backend Django en PythonAnywhere

Esta guía detalla el procedimiento paso a paso para desplegar la API REST de **CodeLab Stock** (Django 6.0 + DRF + MySQL) en la plataforma **PythonAnywhere** bajo una cuenta gratuita (*Beginner*) con certificado HTTPS automático.

---

## 📋 Requisitos Previos

1. Cuenta registrada en [PythonAnywhere](https://www.pythonanywhere.com/).
2. Acceso al repositorio del proyecto en GitHub: `https://github.com/ISPC-WEB-2025/CodeLab.git`.
3. Tu nombre de usuario de PythonAnywhere (en esta guía representado como `<tu_usuario>`).

---

## 🗄️ Paso 1: Configurar la Base de Datos MySQL en PythonAnywhere

PythonAnywhere provee un servidor MySQL gratuito y nativo en la pestaña **Databases**:

1. Ingresá a la pestaña **Databases** en el panel superior.
2. En **"Set your MySQL password"**, definí una contraseña segura para tu servidor MySQL y guardala.
3. En **"Create a database"**, ingresá el nombre `todostock_db` y hacé clic en **Check**.
   * PythonAnywhere prefijará automáticamente el nombre con tu usuario: `<tu_usuario>$todostock_db`.
4. Tomá nota de los datos de conexión que aparecen en pantalla:
   * **Host:** `<tu_usuario>.mysql.pythonanywhere-services.com`
   * **User:** `<tu_usuario>`
   * **Database name:** `<tu_usuario>$todostock_db`
   * **Port:** `3306`

---

## 💻 Paso 2: Clonar el Repositorio desde la Consola Bash

1. Dirigite a la pestaña **Consoles** en el panel superior.
2. Hacé clic en **Bash** para abrir una terminal remota.
3. Cloná el repositorio del proyecto en tu directorio raíz:
   ```bash
   git clone https://github.com/ISPC-WEB-2025/CodeLab.git
   cd CodeLab/Backend
   ```

---

## 🐍 Paso 3: Crear el Entorno Virtual e Instalar Dependencias

Desde la terminal Bash en `~/CodeLab/Backend`:

1. Creá el entorno virtual con Python 3.10:
   ```bash
   python3.10 -m venv venv
   ```
2. Activá el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
3. Actualizá `pip` e instalá las dependencias del proyecto:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔐 Paso 4: Configurar Variables de Entorno (`.env`)

En `~/CodeLab/Backend`, creá el archivo de configuración a partir del modelo provisto:

```bash
cp ".env modelo" .env
nano .env
```

Configurá los valores reales para tu entorno de PythonAnywhere:

```env
# Configuración general
SECRET_KEY="generar_clave_larga_y_segura_aqui"
DEBUG=False
ALLOWED_HOSTS="<tu_usuario>.pythonanywhere.com, localhost"

# Base de datos MySQL en PythonAnywhere
DB_NAME="<tu_usuario>$todostock_db"
DB_USER="<tu_usuario>"
DB_PASSWORD="tu_password_mysql_definido_en_paso_1"
DB_HOST="<tu_usuario>.mysql.pythonanywhere-services.com"
DB_PORT=3306

# Superadministrador inicial (blindado según Issue #261)
ADMIN_EMAIL="admin@codelab.com"
ADMIN_PASSWORD="TuPasswordSeguro2026!"
```

> **Nota:** Para guardar y salir de `nano`: presioná `Ctrl + O`, luego `Enter`, y finalmente `Ctrl + X`.

---

## ⚡ Paso 5: Inicializar la Base de Datos y Recolectar Archivos Estáticos

Con el entorno virtual activo (`source venv/bin/activate`) y dentro de `~/CodeLab/Backend`:

1. Ejecutá el script de inicialización de base de datos (creará tablas, aplicará migraciones, cargará roles y sembrará el superadmin seguro):
   ```bash
   python setup_db.py
   ```
2. Recolectá los archivos estáticos requeridos por el admin de Django y DRF:
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## 🌐 Paso 6: Configurar la Aplicación Web en el Panel de PythonAnywhere

1. Dirigite a la pestaña **Web** en el panel superior.
2. Hacé clic en **"Add a new web app"**.
3. Seleccioná **"Manual configuration"** (NO selecciones Django genérico, para conservar la configuración de nuestro repositorio).
4. Elegí **Python 3.10**.
5. Completá las siguientes secciones en la pantalla de configuración:

### A. Sección Code
* **Source code:** `/home/<tu_usuario>/CodeLab/Backend`
* **Working directory:** `/home/<tu_usuario>/CodeLab/Backend`
* **WSGI configuration file:** 
  * Hacé clic en el enlace `/var/www/<tu_usuario>_pythonanywhere_com_wsgi.py`.
  * Borrá todo el contenido por defecto del archivo.
  * Pegá el contenido de `Backend/config/wsgi_pythonanywhere.py`:
    ```python
    import os
    import sys

    path = os.path.expanduser('~/CodeLab/Backend')
    if path not in sys.path:
        sys.path.append(path)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    ```
  * Hacé clic en el botón verde **Save** (arriba a la derecha) y volvé a la pestaña **Web**.

### B. Sección Virtualenv
* En el campo **Enter path to a virtualenv**, ingresá:
  ```text
  /home/<tu_usuario>/CodeLab/Backend/venv
  ```
  *(Presioná el botón de verificación azul para confirmar)*.

### C. Sección Static files
Agregá la siguiente regla de mapeo:
* **URL:** `/static/`
* **Directory:** `/home/<tu_usuario>/CodeLab/Backend/staticfiles`

### D. Seguridad HTTPS
* Asegurate de que la opción **"Force HTTPS"** esté activada (**Enabled**).

---

## 🚀 Paso 7: Recargar y Probar la Aplicación

1. En la parte superior de la pestaña **Web**, hacé clic en el botón verde grande:
   **"Reload <tu_usuario>.pythonanywhere.com"**.
2. Abrí una pestaña en tu navegador y visitá tu API:
   * **Panel Administrativo:** `https://<tu_usuario>.pythonanywhere.com/admin/`
   * **Endpoint de Autenticación:** `https://<tu_usuario>.pythonanywhere.com/api/usuarios/login/`
   * **Catálogo de Productos:** `https://<tu_usuario>.pythonanywhere.com/api/inventario/productos/`

---

## 🔄 Actualizaciones Futuras (Despliegue Continuo)

Cada vez que se suban cambios a la rama `develop` o `main`:
1. Abrí la consola Bash en PythonAnywhere.
2. Ejecutá:
   ```bash
   cd ~/CodeLab/Backend
   git pull origin develop
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
3. En la pestaña **Web**, hacé clic en **Reload**.
