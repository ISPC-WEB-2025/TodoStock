import string
from unittest.mock import patch
from django.test import TestCase, override_settings
from usuarios.models import Usuario, Role
from scripts.crear_superadmin import crear_superadmin, generar_password_seguro


class CrearSuperadminSecurityTests(TestCase):
    def setUp(self):
        # Aseguramos rol base
        Role.objects.get_or_create(
            nombre="ADMINISTRADOR",
            defaults={"descripcion": "Rol con control total del sistema"},
        )

    def test_generar_password_seguro_structure(self):
        """Valida que la contraseña generada cumpla criterios de alta entropía."""
        pwd = generar_password_seguro(24)
        self.assertEqual(len(pwd), 24)
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))
        self.assertTrue(any(c in "!@#$%&*-_=+" for c in pwd))

    @override_settings(DEBUG=True)
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_dev_default(self, mock_config):
        """En modo desarrollo (DEBUG=True) y sin variables en .env usa credenciales de desarrollo por defecto."""
        mock_config.side_effect = lambda key, default="": ""

        resultado = crear_superadmin()

        self.assertEqual(resultado["email"], "admin@codelab.com")
        self.assertEqual(resultado["password"], "AdminPassword123!")
        self.assertFalse(resultado["autogenerada"])

        user = Usuario.objects.get(email="admin@codelab.com")
        self.assertTrue(user.check_password("AdminPassword123!"))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.rol.nombre, "ADMINISTRADOR")

    @override_settings(DEBUG=True)
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_custom_env(self, mock_config):
        """Si existen variables en .env, se utilizan sin importar el modo."""
        def fake_config(key, default=""):
            if key == "ADMIN_EMAIL":
                return "custom_admin@empresa.com"
            if key == "ADMIN_PASSWORD":
                return "ClaveSuperSegura2026!"
            return default

        mock_config.side_effect = fake_config

        resultado = crear_superadmin()

        self.assertEqual(resultado["email"], "custom_admin@empresa.com")
        self.assertEqual(resultado["password"], "ClaveSuperSegura2026!")
        self.assertFalse(resultado["autogenerada"])

        user = Usuario.objects.get(email="custom_admin@empresa.com")
        self.assertTrue(user.check_password("ClaveSuperSegura2026!"))
        self.assertTrue(user.is_superuser)

    @override_settings(DEBUG=False)
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_prod_generates_random_password(self, mock_config):
        """En producción (DEBUG=False) y sin contraseña configurada, autogenera una segura."""
        mock_config.side_effect = lambda key, default="": ""

        resultado = crear_superadmin()

        self.assertEqual(resultado["email"], "admin@codelab.com")
        self.assertTrue(resultado["autogenerada"])
        self.assertGreaterEqual(len(resultado["password"]), 20)

        user = Usuario.objects.get(email="admin@codelab.com")
        self.assertTrue(user.check_password(resultado["password"]))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @override_settings(DEBUG=False)
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_prod_with_custom_password(self, mock_config):
        """En producción con contraseña explícita en .env, respeta la contraseña provista."""
        def fake_config(key, default=""):
            if key == "ADMIN_PASSWORD":
                return "ClaveProduccionExplícita2026#"
            return default

        mock_config.side_effect = fake_config

        resultado = crear_superadmin()

        self.assertFalse(resultado["autogenerada"])
        self.assertEqual(resultado["password"], "ClaveProduccionExplícita2026#")
        user = Usuario.objects.get(email="admin@codelab.com")
        self.assertTrue(user.check_password("ClaveProduccionExplícita2026#"))

    @override_settings(DEBUG=True)
    def test_crear_superadmin_idempotent(self):
        """Validar que múltiples ejecuciones no dupliquen usuarios y actualicen credenciales."""
        res1 = crear_superadmin(email_override="idempotent@test.com", password_override="Pass1!")
        self.assertTrue(res1["creado"])

        res2 = crear_superadmin(email_override="idempotent@test.com", password_override="Pass2!")
        self.assertFalse(res2["creado"])

        self.assertEqual(Usuario.objects.filter(email="idempotent@test.com").count(), 1)
        user = Usuario.objects.get(email="idempotent@test.com")
        self.assertTrue(user.check_password("Pass2!"))
