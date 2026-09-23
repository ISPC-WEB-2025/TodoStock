import subprocess
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()
import MySQLdb

from django.conf import settings
from django.db import connection

db = settings.DATABASES["default"]
try:
    conn = MySQLdb.connect(
        host=db["HOST"],
        user=db["USER"],
        passwd=db["PASSWORD"],
        port=int(db.get("PORT") or 3306),
    )
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {db['NAME']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Base de datos creada o verificada.")
except Exception as e:
    print(f"ℹ️ Verificación de CREATE DATABASE omitida ({e}). Se utilizará la base preexistente.")


def run_sql(file):
    print(f"Ejecutando {file}...")
    with open(file, "r", encoding="utf-8") as f:
        sql = f.read()
    with connection.cursor() as cursor:
        for statement in sql.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            first_word = statement.split()[0].upper() if statement.split() else ""
            # Omitir sentencias 'USE ...' y 'CREATE DATABASE ...' para operar siempre sobre la base activa de Django
            if first_word == "USE" or statement.upper().startswith("CREATE DATABASE"):
                continue
            cursor.execute(statement)
    connection.commit()


print("1. Ejecutando estructura base...")
run_sql("scripts/01_estructura.sql")

print("2. Actualizando registros de migraciones...")
subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)

print("2a. Ejecutando migraciones Django...")
subprocess.run([sys.executable, "manage.py", "migrate"], check=True)

print("2b. Cargando roles base desde roles.json...")
subprocess.run([sys.executable, "manage.py", "loaddata", "roles.json"], check=True)

print("3. Creando tabla MOVIMIENTO...")
run_sql("scripts/02_movimiento.sql")

print("4. Insertando datos de prueba...")
run_sql("scripts/03_datos.sql")

print("5. Creando usuario superadmin por defecto...")
from scripts.crear_superadmin import crear_superadmin
crear_superadmin()

print("✅ Base de datos lista.")
