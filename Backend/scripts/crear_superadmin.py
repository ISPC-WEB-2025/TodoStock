import os
import sys
import secrets
import string
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configurar entorno de Django si no está inicializado
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

if not django.apps.apps.ready:
    django.setup()

from decouple import config
from django.conf import settings
from usuarios.models import Usuario, Role


def generar_password_seguro(longitud: int = 20) -> str:
    """
    Genera una contraseña criptográficamente segura de alta entropía
    con garantía de mayúsculas, minúsculas, dígitos y caracteres especiales.
    """
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    especiales = "!@#$%&*-_=+"
    todos = minusculas + mayusculas + digitos + especiales

    # Asegurar al menos un caracter de cada conjunto
    pwd = [
        secrets.choice(minusculas),
        secrets.choice(mayusculas),
        secrets.choice(digitos),
        secrets.choice(especiales),
    ]
    pwd += [secrets.choice(todos) for _ in range(longitud - 4)]

    # Mezcla criptográfica para evitar patrones en las posiciones iniciales
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def crear_superadmin(
    email_override: str | None = None,
    password_override: str | None = None,
) -> dict:
    """
    Crea o actualiza el usuario superadministrador del sistema.
    Lee las credenciales desde variables de entorno (ADMIN_EMAIL, ADMIN_PASSWORD).
    En entornos con DEBUG=False, si no se especifica ADMIN_PASSWORD, genera una
    contraseña segura aleatoria de alta entropía y la notifica por consola.
    """
    rol_admin, _ = Role.objects.get_or_create(
        nombre="ADMINISTRADOR",
        defaults={"descripcion": "Rol con control total del sistema"},
    )

    is_debug = getattr(settings, "DEBUG", True)

    # 1. Determinar Email
    email_env = config("ADMIN_EMAIL", default="").strip()
    email = email_override or email_env or "admin@codelab.com"

    # 2. Determinar Password
    pwd_env = config("ADMIN_PASSWORD", default="").strip()
    pwd_input = password_override or (pwd_env if pwd_env else None)

    autogenerada = False
    if pwd_input:
        password = pwd_input
        if not is_debug and password == "AdminPassword123!":
            print("\n[ALERTA DE SEGURIDAD] DEBUG=False pero se esta usando la contrasena")
            print("   por defecto 'AdminPassword123!'. Se recomienda cambiarla inmediatamente.\n")
    else:
        if is_debug:
            password = "AdminPassword123!"
            print(f"\n[MODO DESARROLLO] Se utilizo la contrasena de desarrollo por defecto para {email}.")
        else:
            password = generar_password_seguro(20)
            autogenerada = True

    dni = "12345678"
    nombre = "Super Admin"

    user, created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            "nombre": nombre,
            "dni": dni,
            "fecha_nacimiento": "1990-01-01",
            "rol": rol_admin,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    user.nombre = nombre
    user.dni = dni
    user.rol = rol_admin
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    print("\n========================================================")
    print("        USUARIO SUPERADMINISTRADOR CONFIGURADO          ")
    print("========================================================")
    print(f"  Email:        {email}")
    if autogenerada:
        print(f"  Password:     {password}  <-- AUTOGENERADA (ALTA ENTROPIA)")
        print("  [!] ATENCION: Guarda esta contrasena en un lugar seguro.")
        print("      No volvera a mostrarse en texto plano.")
    elif is_debug and not pwd_input:
        print(f"  Password:     {password}  (Credencial de desarrollo)")
    else:
        print("  Password:     [CONFIGURADA DESDE VARIABLES DE ENTORNO]")
    print(f"  Rol:          {rol_admin.nombre}")
    print(f"  Superusuario: {user.is_superuser}")
    print("========================================================\n")

    return {
        "usuario": user,
        "email": email,
        "password": password,
        "autogenerada": autogenerada,
        "creado": created,
    }


if __name__ == "__main__":
    crear_superadmin()
