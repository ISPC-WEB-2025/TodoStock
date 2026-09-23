# 🚀 Guía Definitiva: Cómo Desplegar Cualquier App de Django en Alwaysdata

Esta guía está diseñada paso a paso para desplegar **cualquier proyecto Django** en el servicio de hosting gratuito de **Alwaysdata**, utilizando **MySQL/MariaDB**, **Python 3.12**, **WSGI** y **WhiteNoise** para asegurar que los estilos visuales del administrador carguen a la perfección.

---

## 📋 Requisitos Previos

1. Cuenta registrada en [Alwaysdata](https://www.alwaysdata.com/).
2. Tu repositorio de Django subido a GitHub (público o con credenciales de acceso).
3. Tu nombre de cuenta de Alwaysdata (en esta guía nos referiremos a él como `<tu_usuario>`).

---

## 🗄️ Paso 1: Configurar MySQL y la Base de Datos en Alwaysdata

*(Si tu aplicación usa SQLite podés saltear este paso, pero para producción MySQL/MariaDB es lo recomendado).*

1. En el menú lateral izquierdo de Alwaysdata, hacé clic en **Databases ➔ MySQL**.
2. **Configuración inicial del usuario:**
   * La primera vez que ingresás, Alwaysdata te pedirá directamente configurar o inicializar tu usuario de base de datos y definirle una contraseña.
   * Ingresá una contraseña segura que recuerdes y anotala (la vas a usar en el paso de variables de entorno).
   *(Si el usuario ya estaba creado de antes: andá a la pestaña **USERS**, hacé clic en la tuerquita de tu usuario y asignale la contraseña ahí).*
3. **Crear la Base de Datos:**
   * En la misma sección, hacé clic en la pestaña **DATABASES**.
   * Clic en el botón **+ Add a database** (arriba a la derecha).
   * **Name:** Ingresá un nombre identificatorio (ej: `miapp_db` o el nombre de tu proyecto).
   * En la lista de usuarios con permisos, asegurate de que tu usuario tenga marcados todos los permisos sobre esta base.
   * Clic en **Submit** (Guardar).

> 📌 **Tus datos de conexión serán:**
> * **Host:** `mysql-<tu_usuario>.alwaysdata.net`
> * **Usuario:** `<tu_usuario>`
> * **Contraseña:** La que definiste recién.
> * **Base de datos:** `<el_nombre_que_le_pusiste>`
> * **Puerto:** `3306`

---

## 💻 Paso 2: Abrir la Terminal Web (Web SSH)

Alwaysdata incluye una terminal Linux directamente en el navegador:

1. En el menú lateral izquierdo, andá a **Remote access ➔ SSH/SFTP**.
2. En el recuadro amarillo superior, hacé clic en el enlace que dice **on the Web** (o en el ícono `>_` al final de la fila de tu usuario).
3. Se abrirá una pestaña o ventana negra de terminal. Si te pide credenciales:
   * **Login:** Tu nombre de usuario de Alwaysdata.
   * **Password:** La contraseña general de tu cuenta de Alwaysdata.

---

## 📦 Paso 3: Clonar el Repositorio y Crear el Entorno Virtual

En la terminal negra, ejecutá los siguientes comandos reemplazando la URL con la de tu repositorio:

```bash
# 1. Clonar el repositorio de GitHub
git clone https://github.com/<tu_usuario_o_organizacion>/<tu_repositorio>.git

# 2. Entrar a la carpeta donde reside manage.py
# (Atención: Linux distingue mayúsculas de minúsculas)
cd <tu_repositorio>

# Si tu archivo manage.py está dentro de una subcarpeta (ej: Backend/):
# cd <tu_repositorio>/Backend

# 3. Crear el entorno virtual con Python 3.12 (versión moderna y estable en Alwaysdata)
python3.12 -m venv venv

# 4. Activar el entorno virtual
source venv/bin/activate

# 5. Actualizar pip e instalar dependencias del proyecto
pip install --upgrade pip
pip install -r requirements.txt
```

*(Cuando el entorno esté activo, notarás que el prompt de la terminal comienza con `(venv)`)*.

---

## 🔐 Paso 4: Configurar Variables de Entorno (`.env`)

Si tu aplicación utiliza variables de entorno (`python-decouple`, `django-environ` o archivo `.env`):

Estando en la misma carpeta que `manage.py`, ejecutá este comando en bloque para crear el archivo `.env`:

```bash
cat << 'EOF' > .env
SECRET_KEY="tu_clave_secreta_larga_y_aleatoria_para_django!"
DEBUG=False
ALLOWED_HOSTS="<tu_usuario>.alwaysdata.net, localhost"

# Conexión MySQL de Alwaysdata
DB_NAME="<nombre_base_creada_en_paso_1>"
DB_USER="<tu_usuario>"
DB_PASSWORD="<contraseña_de_mysql_del_paso_1>"
DB_HOST="mysql-<tu_usuario>.alwaysdata.net"
DB_PORT=3306
EOF
```

> ⚠️ **Recomendaciones importantes**:
> * **Comillas obligatorias:** Envolvé siempre las contraseñas entre comillas dobles `""`. Si una clave incluye caracteres como `#` o `!`, sin comillas el sistema podría interpretarlo como comentario y cortarla.
> * **ALLOWED_HOSTS:** Es obligatorio incluir `<tu_usuario>.alwaysdata.net` para que Django acepte las solicitudes que lleguen a tu dominio.

---

## 🎨 Paso 5: Configurar WhiteNoise (Para que el Admin no pierda estilos CSS)

En la mayoría de los hostings compartidos, el servidor web no entrega los archivos de la carpeta `/static/` por defecto, provocando que el panel `/admin/` se vea como texto plano sin diseño. La solución estándar en la industria es **WhiteNoise**:

1. En la terminal (con `venv` activo), instalá la librería:
   ```bash
   pip install whitenoise
   ```
2. Asegurate de incluirla en tu código:
   * En `settings.py`, dentro de `MIDDLEWARE`, agregá `'whitenoise.middleware.WhiteNoiseMiddleware'` justo debajo de `SecurityMiddleware`:
     ```python
     MIDDLEWARE = [
         'django.middleware.security.SecurityMiddleware',
         'whitenoise.middleware.WhiteNoiseMiddleware',
         ...
     ]
     ```
   * En `settings.py`, asegurate de tener definidos:
     ```python
     STATIC_URL = '/static/'
     STATIC_ROOT = BASE_DIR / 'staticfiles'
     ```

---

## ⚡ Paso 6: Migraciones, Superusuario y Recolección de Estáticos

En la terminal (con `venv` activo), ejecutá:

```bash
# 1. Aplicar las migraciones para crear las tablas en MySQL
python manage.py migrate

# 2. Crear tu usuario Administrador (para acceder a /admin/)
python manage.py createsuperuser

# 3. Recolectar todos los archivos estáticos (CSS, JS, imágenes)
python manage.py collectstatic --noinput
```

---

## 🌐 Paso 7: Configurar el Servidor Web (WSGI) en Alwaysdata

1. En el panel de Alwaysdata, andá al menú lateral: **Web ➔ Sites**.
2. Hacé clic en la **tuerquita / lápiz (Edit)** de tu sitio principal (`<tu_usuario>.alwaysdata.net`).
3. Completá los campos según esta tabla:

| Campo | Qué colocar | Ejemplo ilustrativo |
| --- | --- | --- |
| **Addresses** | Tu dominio de Alwaysdata | `usuario.alwaysdata.net`<br>*(Si hay una fila vacía debajo, hacé clic en el botón Delete para quitarla)* |
| **Type** | Seleccionar: **Python WSGI** | Python WSGI |
| **Application path** | Ruta hacia el archivo `wsgi.py` | `<repo>/<proyecto>/wsgi.py`<br>*(ej: `CodeLab/Backend/config/wsgi.py`)* |
| **Working directory** | Carpeta donde reside `manage.py` | `<repo>/`<br>*(ej: `CodeLab/Backend/`)* |
| **Environment variables** | Dejar vacío | *(Django lee el `.env` automáticamente)* |
| **Python version** | Seleccionar: **3.12** | 3.12 |
| **virtualenv directory** | Ruta a la carpeta `venv` | `<repo>/venv`<br>*(ej: `CodeLab/Backend/venv`)* |
| **Static paths** | **DEJARLO VACÍO** | *(WhiteNoise se encarga de servir los estáticos directamente desde Django sin intermediarios)* |

> 💡 **Nota sobre las rutas**: Notarás que el formulario de Alwaysdata ya coloca `/home/<tu_usuario>/` fijo en color gris fuera de la caja de texto. En la caja solo debés escribir lo que continúa a partir de allí.

4. Bajá al final de la página y hacé clic en el botón verde **Submit** (Guardar).

---

## ✅ Paso 8: Verificación en el Navegador

Abrí una pestaña en tu navegador e ingresá a:

* **Tu Sitio Web:** `https://<tu_usuario>.alwaysdata.net/`
* **Panel de Administración:** `https://<tu_usuario>.alwaysdata.net/admin/`

Iniciá sesión con las credenciales creadas con `createsuperuser`. Verás el panel con todo su diseño visual, tipografías y estilos cargados de forma óptima.

---

## 💡 Preguntas Frecuentes y Errores Comunes

1. **Error 400 Bad Request:**  
   Revisá que el dominio `<tu_usuario>.alwaysdata.net` esté presente en la lista de `ALLOWED_HOSTS` de tu archivo `.env` o en `settings.py`.
2. **Error 500 / DisallowedHost:**  
   Consultá los registros de error en el panel de Alwaysdata (**Web ➔ Sites ➔ Logs**) para ver el detalle exacto del fallo en Python.
3. **El panel admin se ve en blanco y negro sin estilos:**  
   Verificá haber ejecutado `python manage.py collectstatic --noinput` y que `WhiteNoiseMiddleware` esté registrado en `settings.py`. Además, asegurate de que el campo **Static paths** de Alwaysdata esté completamente vacío para que no interfiera.
4. **Mayúsculas y minúsculas en Linux:**  
   A diferencia de Windows, Linux es estricto con las mayúsculas. Si la carpeta en GitHub es `MiProyecto`, `cd miproyecto` fallará indicando que el directorio no existe.
