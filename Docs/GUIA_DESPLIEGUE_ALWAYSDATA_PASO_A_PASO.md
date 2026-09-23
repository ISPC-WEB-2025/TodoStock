# 🚀 Guía de Despliegue de Backend Django en Alwaysdata (Paso a Paso)

Esta guía documenta el procedimiento completo y probado para desplegar el backend de **TodoStock (CodeLab)** en la plataforma **Alwaysdata**, utilizando **MySQL/MariaDB**, **Python 3.12**, **WSGI** y **WhiteNoise** para los archivos estáticos.

---

## 📋 Requisitos Previos

1. Una cuenta activa y gratuita en [Alwaysdata](https://www.alwaysdata.com/).
2. Acceso al repositorio en GitHub: `https://github.com/ISPC-WEB-2025/CodeLab.git`.
3. Tu nombre de cuenta de Alwaysdata (ejemplo: `todostock`).

---

## 🗄️ Paso 1: Configurar la Base de Datos MySQL en Alwaysdata

1. Iniciá sesión en el panel de control de Alwaysdata.
2. En el menú lateral izquierdo, andá a **Databases ➔ MySQL**.
3. **Crear la Base de Datos:**
   * Hacé clic en la pestaña **DATABASES**.
   * Clic en el botón **+ Add a database** (arriba a la derecha).
   * En **Name**, escribí: `todostock_db`.
   * Clic en **Submit**.
4. **Configurar Contraseña y Permisos del Usuario:**
   * Hacé clic en la pestaña **USERS** (al lado de DATABASES).
   * Vas a ver a tu usuario principal (mismo nombre que tu cuenta, ej: `todostock`).
   * Hacé clic en el ícono de la **tuerquita / lápiz (Edit)** de esa fila.
   * En el campo **Password**, ingresá una contraseña segura que recuerdes (ej: `TuPasswordSeguro2026!`).
   * En la sección **Permissions**, asegurate de marcar los permisos sobre la base `todostock_db`.
   * Clic en **Submit** para guardar.

> 💡 **Nota importante**: Tu host de base de datos será siempre `mysql-<tu_usuario>.alwaysdata.net` (ej: `mysql-todostock.alwaysdata.net`).

---

## 💻 Paso 2: Abrir la Terminal Web (Web SSH)

1. En el menú lateral izquierdo de Alwaysdata, andá a **Remote access ➔ SSH/SFTP**.
2. En el recuadro amarillo superior, hacé clic en el enlace que dice **on the Web** (o en el ícono `>_` al final de la fila de tu usuario).
3. Se abrirá una terminal negra en tu navegador. Si te pide credenciales:
   * **Login:** Tu nombre de usuario de Alwaysdata.
   * **Password:** La contraseña de tu cuenta.

---

## 📦 Paso 3: Clonar el Repositorio y Crear el Entorno Virtual

En la terminal negra, ejecutá estos comandos uno por uno (o en bloque):

```bash
# 1. Clonar el repositorio (usamos develop para pruebas o main para producción)
git clone -b develop https://github.com/ISPC-WEB-2025/CodeLab.git

# 2. Entrar a la carpeta del Backend (respetando mayúsculas)
cd CodeLab/Backend

# 3. Crear el entorno virtual con Python 3.12
python3.12 -m venv venv

# 4. Activar el entorno virtual
source venv/bin/activate

# 5. Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

*(Una vez activado el entorno, el prompt de la terminal mostrará el prefijo `(venv)`)*.

---

## 🔐 Paso 4: Crear el Archivo de Variables de Entorno (`.env`)

En `CodeLab/Backend`, ejecutá el siguiente comando para generar tu archivo `.env` directamente (reemplazá los valores entre `<...>` con tus datos reales):

```bash
cat << 'EOF' > .env
SECRET_KEY="c0d3l4b_s3cur3_k3y_pr0duct10n_st0ck_2026!"
DEBUG=False
ALLOWED_HOSTS="<tu_usuario>.alwaysdata.net, localhost"
DB_NAME="todostock_db"
DB_USER="<tu_usuario>"
DB_PASSWORD="<tu_contraseña_de_mysql_del_paso_1>"
DB_HOST="mysql-<tu_usuario>.alwaysdata.net"
DB_PORT=3306
ADMIN_EMAIL="<tu_email_personal>@gmail.com"
ADMIN_PASSWORD="<TuPasswordParaEntrarAlAdmin2026!>"
EOF
```

> ⚠️ **Recomendación de seguridad**:
> * Siempre envolvé los valores entre comillas dobles `""`, especialmente las contraseñas. Si una contraseña contiene caracteres especiales como `#`, sin comillas podría ser interpretada como un comentario y cortarse.
> * `ADMIN_EMAIL` y `ADMIN_PASSWORD` serán las credenciales con las que iniciarás sesión en el panel `/admin/` y en el frontend.

---

## ⚡ Paso 5: Inicializar la Base de Datos y Recolectar Estáticos

Con el entorno virtual activo (`(venv)`):

```bash
# 1. Crear tablas, roles, datos iniciales y superadministrador
python setup_db.py

# 2. Compilar y recolectar los archivos estáticos (CSS/JS)
python manage.py collectstatic --noinput
```

*(La advertencia `MariaDB Strict Mode is not set` es solo informativa y normal en hostings compartidos. Al finalizar verás `✅ Base de datos lista` y las credenciales del admin).*

---

## 🌐 Paso 6: Configurar el Servidor Web (WSGI) en Alwaysdata

1. En el menú lateral izquierdo de Alwaysdata, andá a **Web ➔ Sites**.
2. Hacé clic en la **tuerquita / lápiz (Edit)** de tu sitio por defecto (`<tu_usuario>.alwaysdata.net`).
3. Configurá los campos exactamente como sigue:

| Campo | Valor |
| --- | --- |
| **Addresses** | Debe quedar solo `<tu_usuario>.alwaysdata.net` (si hay una fila vacía debajo, hacé clic en *Delete* para borrarla). |
| **Type** | Seleccioná **Python WSGI**. |
| **Application path** | `CodeLab/Backend/config/wsgi.py` *(el prefijo `/home/<tu_usuario>/` ya viene fijo afuera)* |
| **Working directory** | `CodeLab/Backend/` *(el prefijo `/home/<tu_usuario>/` ya viene fijo afuera)* |
| **Environment variables** | *Dejar vacío* (Django lee el archivo `.env` automáticamente). |
| **Python version** | Seleccioná **3.12**. |
| **virtualenv directory** | `CodeLab/Backend/venv` |
| **Static paths** | **DEJARLO VACÍO**. *(Gracias a WhiteNoise, Django sirve sus propios estáticos sin necesidad de configuración en el hosting).* |

4. Bajá hasta el fondo de la página y hacé clic en el botón verde **Submit** (o Guardar).

---

## ✅ Paso 7: Verificación en el Navegador

Abrí tu navegador web e ingresá a:

1. **Panel de Administración:**
   * URL: `https://<tu_usuario>.alwaysdata.net/admin/`
   * Iniciá sesión con tu `ADMIN_EMAIL` y `ADMIN_PASSWORD`.
   * Debe cargar con el diseño visual azul/oscuro estilizado completo (CSS activo vía WhiteNoise).
2. **API de Productos (REST):**
   * URL: `https://<tu_usuario>.alwaysdata.net/api/inventario/productos/`
   * Debe responder con error de seguridad `401 Unauthorized` (confirmando que la protección JWT está activa).

---

## 🔀 Paso 8: El Flujo GitFlow Hacia Producción (`main`)

Una vez que comprobaste que el despliegue funciona al 100% en `develop`, se formaliza la entrega:

1. **Crear la rama de release desde `develop`:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.0.0
   git push -u origin release/v1.0.0
   ```
2. **Abrir Pull Request en GitHub:**
   * Base: `main` ➔ Compare: `release/v1.0.0`
   * Título: `release: MVP v1.0.0`
   * Mergear hacia `main`.
3. **Publicar el Release en GitHub:**
   * Ir a la sección **Releases** en GitHub ➔ **Draft a new release**.
   * Tag: `v1.0.0` sobre `main`.
   * Título: `TodoStock MVP v1.0.0`.
   * Clic en **Generate release notes** ➔ **Publish release**.
4. **Actualizar el servidor de Alwaysdata a `main`:**
   En la terminal SSH:
   ```bash
   cd ~/CodeLab/Backend
   git checkout main
   git pull origin main
   ```
   *(El servidor de Alwaysdata queda oficialmente siguiendo la rama estable de producción).*

---

## 🛠️ Lecciones Aprendidas y Solución de Problemas Frecuentes

1. **Error 1044: Access denied to database:**  
   Ocurre si en los scripts SQL hay sentencias fijas como `USE todostock;` cuando en el hosting la base se llama distinto (ej: `todostock_db`). El script `setup_db.py` actual filtra automáticamente los comandos `USE` para operar sobre la conexión activa de Django.
2. **Admin sin estilos (HTML plano en blanco y negro):**  
   Ocurre cuando el hosting no mapea adecuadamente la carpeta `/static/`. Se resolvió definitivamente incorporando la librería `whitenoise`, permitiendo que Django entregue de forma autónoma todos los archivos estáticos comprimidos.
3. **Mayúsculas en Linux:**  
   La carpeta del proyecto es `CodeLab` (con **C** y **L** mayúsculas). En Linux no es lo mismo que `codelab`.
