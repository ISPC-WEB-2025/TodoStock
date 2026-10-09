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
    @patch("scripts.crear_superadmin.getpass.getpass")
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_dev_sin_password_pide_consola(self, mock_config, mock_getpass):
        """TK45: en desarrollo y sin ADMIN_PASSWORD, pide contraseña interactiva."""
        mock_config.side_effect = lambda key, default="": ""
        mock_getpass.return_value = "ClaveSimuladaParaTest123!"

        resultado = crear_superadmin()

        self.assertEqual(resultado["email"], "admin@codelab.com")
        self.assertFalse(resultado["autogenerada"])
        self.assertEqual(resultado["password"], "ClaveSimuladaParaTest123!")

        user = Usuario.objects.get(email="admin@codelab.com")
        self.assertTrue(user.check_password("ClaveSimuladaParaTest123!"))
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
    @patch("scripts.crear_superadmin.getpass.getpass")
    @patch("scripts.crear_superadmin.config")
    def test_crear_superadmin_prod_pide_consola(self, mock_config, mock_getpass):
        """En producción (DEBUG=False) y sin contraseña configurada, pide por consola."""
        mock_config.side_effect = lambda key, default="": ""
        mock_getpass.return_value = "ClaveSimuladaParaTest123!"

        resultado = crear_superadmin()

        self.assertEqual(resultado["email"], "admin@codelab.com")
        self.assertFalse(resultado["autogenerada"])
        self.assertEqual(resultado["password"], "ClaveSimuladaParaTest123!")

        user = Usuario.objects.get(email="admin@codelab.com")
        self.assertTrue(user.check_password("ClaveSimuladaParaTest123!"))
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

    @override_settings(DEBUG=True)
    def test_crear_superadmin_dni_collision_handled(self):
        """Si otro usuario ya tiene el DNI 12345678, asigna uno alternativo sin romper la restricción UNIQUE."""
        # Creamos un usuario previo con el DNI por defecto
        Usuario.objects.create_user(
            email="otro_usuario@test.com",
            nombre="Otro Usuario",
            dni="12345678",
            fecha_nacimiento="1992-02-02",
            password="OtherPassword123!",
        )

        # crear_superadmin no debe fallar con IntegrityError
        res = crear_superadmin(email_override="admin_conflict@test.com", password_override="AdminPass123!")
        self.assertTrue(res["creado"])
        admin_user = Usuario.objects.get(email="admin_conflict@test.com")
        self.assertTrue(admin_user.is_superuser)
        self.assertNotEqual(admin_user.dni, "12345678")
        self.assertTrue(admin_user.dni.startswith("99"))
