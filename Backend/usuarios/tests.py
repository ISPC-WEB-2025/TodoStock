from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Usuario, Role


class JWTAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role_admin = Role.objects.create(
            nombre="ADMINISTRADOR", descripcion="Administrador general"
        )
        self.role_vendedor = Role.objects.create(
            nombre="VENTAS", descripcion="Vendedor de salón"
        )
        self.admin_user = Usuario.objects.create_user(
            email="admin@test.com",
            nombre="Admin Test",
            dni="12345678",
            fecha_nacimiento="1990-01-01",
            password="adminpassword123",
            rol=self.role_admin,
            is_staff=True,
            is_superuser=True,
        )
        self.vendedor_user = Usuario.objects.create_user(
            email="vendedor@test.com",
            nombre="Vendedor Test",
            dni="87654321",
            fecha_nacimiento="1995-05-15",
            password="vendedorpassword123",
            rol=self.role_vendedor,
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            "/api/usuarios/login/",
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["nombre"], "Admin Test")
        self.assertTrue(response.data["es_admin"])

    def test_token_refresh_endpoint(self):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "vendedor@test.com", "password": "vendedorpassword123"},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        refresh_token = login_resp.data["refresh"]

        refresh_resp = self.client.post(
            "/api/usuarios/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_resp.data)

    def test_protected_endpoint_with_bearer_token(self):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )
        access_token = login_resp.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/usuarios/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_endpoint_rejects_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token_12345")
        response = self.client.get("/api/usuarios/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AutoservicioPasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role_emp = Role.objects.create(nombre="EMPLEADO", descripcion="Empleado general")
        self.user = Usuario.objects.create_user(
            email="empleado@test.com",
            nombre="Empleado Uno",
            dni="99887766",
            fecha_nacimiento="1992-03-10",
            password="PasswordVieja1!",
            rol=self.role_emp,
        )
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "empleado@test.com", "password": "PasswordVieja1!"},
            format="json",
        )
        self.token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_change_password_success(self):
        resp = self.client.post(
            "/api/usuarios/me/change-password/",
            {
                "password_actual": "PasswordVieja1!",
                "nueva_password": "PasswordNueva2026!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("mensaje", resp.data)

        # Verificar que la nueva clave funciona para login
        self.client.credentials()  # desautenticar
        login_new = self.client.post(
            "/api/usuarios/login/",
            {"email": "empleado@test.com", "password": "PasswordNueva2026!"},
            format="json",
        )
        self.assertEqual(login_new.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_current(self):
        resp = self.client.post(
            "/api/usuarios/me/change-password/",
            {
                "password_actual": "ClaveIncorrecta999!",
                "nueva_password": "PasswordNueva2026!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.data)

    def test_change_password_rejects_weak_passwords(self):
        # Menor a 9 caracteres
        resp_corta = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "Abc1!"},
            format="json",
        )
        self.assertEqual(resp_corta.status_code, status.HTTP_400_BAD_REQUEST)

        # Sin caracter especial
        resp_sin_simbolo = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "Password1234"},
            format="json",
        )
        self.assertEqual(resp_sin_simbolo.status_code, status.HTTP_400_BAD_REQUEST)

        # Sin numeros
        resp_sin_num = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "PasswordSinNum!"},
            format="json",
        )
        self.assertEqual(resp_sin_num.status_code, status.HTTP_400_BAD_REQUEST)

        # Falso positivo: espacio como carácter especial (ej. "Password 1")
        resp_espacio = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "Password 1"},
            format="json",
        )
        self.assertEqual(resp_espacio.status_code, status.HTTP_400_BAD_REQUEST)

        # Falso positivo: carácter Unicode no ASCII como falso símbolo (ej. "Contrasena9ñ")
        resp_unicode = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "Contrasena9ñ"},
            format="json",
        )
        self.assertEqual(resp_unicode.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_rejects_identical_password(self):
        resp = self.client.post(
            "/api/usuarios/me/change-password/",
            {"password_actual": "PasswordVieja1!", "nueva_password": "PasswordVieja1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.data)

    def test_registro_rejects_weak_password(self):
        self.client.credentials()  # anónimo
        resp = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "Nuevo Usuario",
                "email": "nuevo@test.com",
                "dni": "55667788",
                "fdn": "1999-01-01",
                "password": "123",  # débil
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.data)


class JerarquiaAdministrativaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role_admin = Role.objects.create(nombre="ADMINISTRADOR", descripcion="Admin")
        self.role_emp = Role.objects.create(nombre="EMPLEADO", descripcion="Empleado")

        self.superadmin = Usuario.objects.create_user(
            email="superadmin@test.com",
            nombre="Super Admin",
            dni="11111111",
            fecha_nacimiento="1980-01-01",
            password="SuperPassword1!",
            rol=self.role_admin,
            is_staff=True,
            is_superuser=True,
        )

        self.admin_regular = Usuario.objects.create_user(
            email="admin_regular@test.com",
            nombre="Admin Regular",
            dni="22222222",
            fecha_nacimiento="1985-05-05",
            password="AdminRegular1!",
            rol=self.role_admin,
            is_staff=True,
            is_superuser=False,
        )

        self.otro_admin = Usuario.objects.create_user(
            email="otro_admin@test.com",
            nombre="Otro Admin",
            dni="33333333",
            fecha_nacimiento="1988-08-08",
            password="OtroAdminPass1!",
            rol=self.role_admin,
            is_staff=True,
            is_superuser=False,
        )

        self.empleado = Usuario.objects.create_user(
            email="empleado_op@test.com",
            nombre="Empleado Operativo",
            dni="44444444",
            fecha_nacimiento="1995-10-10",
            password="EmpleadoPass1!",
            rol=self.role_emp,
        )

    def auth_as(self, user, raw_password):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": user.email, "password": raw_password},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_resp.data['access']}")

    def test_admin_cannot_edit_other_admin(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.patch(
            f"/api/usuarios/{self.otro_admin.id}/",
            {"nombre": "Nombre Modificado"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_deactivate_other_admin(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.delete(f"/api/usuarios/{self.otro_admin.id}/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_reset_password_of_other_admin(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.post(
            f"/api/usuarios/{self.otro_admin.id}/reset-password/",
            {"nueva_password": "HackeadaAdmin1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_assign_admin_role(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.patch(
            f"/api/usuarios/{self.empleado.id}/",
            {"rol_id": self.role_admin.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nobody_can_deactivate_superuser(self):
        self.auth_as(self.superadmin, "SuperPassword1!")
        resp = self.client.delete(f"/api/usuarios/{self.superadmin.id}/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_reset_employee_password(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.post(
            f"/api/usuarios/{self.empleado.id}/reset-password/",
            {"nueva_password": "NuevaClaveEmp1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Probar login del empleado con su nueva contraseña
        self.client.credentials()
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "empleado_op@test.com", "password": "NuevaClaveEmp1!"},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    def test_update_ignores_password(self):
        self.auth_as(self.admin_regular, "AdminRegular1!")
        resp = self.client.patch(
            f"/api/usuarios/{self.empleado.id}/",
            {"password": "IgnoradoPass1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verificar que la clave anterior del empleado sigue intacta
        self.client.credentials()
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "empleado_op@test.com", "password": "EmpleadoPass1!"},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)


class AuthRobustezTests(TestCase):
    """
    Tests de robustez y blindaje de autenticación (Issues #294, #295, #296 / ADR-0008).
    - Login de cuenta inactiva retorna 403 ("Cuenta pendiente de aprobación").
    - Login expone campo 'is_superuser'.
    - Superadministrador no puede autodesactivarse vía DELETE /api/usuarios/me/.
    - Usuario regular sí puede autodesactivarse vía DELETE /api/usuarios/me/.
    - Endpoints públicos (login, registro, contacto) funcionan con token inválido en header.
    - Registro rechaza DNI inválido (alfanumérico o longitud distinta de 7-8) con 400.
    - Registro rechaza DNI o email duplicado con 400 JSON sin error 500 HTML.
    """
    def setUp(self):
        self.client = APIClient()
        self.role_op = Role.objects.create(nombre="EMPLEADO", descripcion="Empleado")
        self.superadmin = Usuario.objects.create_user(
            email="super_robust@test.com",
            nombre="Super Robusto",
            dni="10101010",
            fecha_nacimiento="1980-01-01",
            password="SuperPassword1!",
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.usuario_inactivo = Usuario.objects.create_user(
            email="inactivo@test.com",
            nombre="Usuario Inactivo",
            dni="20202020",
            fecha_nacimiento="1990-02-02",
            password="InactivoPassword1!",
            is_active=False,
        )
        self.usuario_activo = Usuario.objects.create_user(
            email="activo@test.com",
            nombre="Usuario Activo",
            dni="30303030",
            fecha_nacimiento="1995-03-03",
            password="ActivoPassword1!",
            rol=self.role_op,
            is_active=True,
        )

    def test_login_inactivo_returns_403(self):
        resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "inactivo@test.com", "password": "InactivoPassword1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", resp.data)
        self.assertEqual(resp.data["error"], "Cuenta pendiente de aprobación por el administrador.")

    def test_login_incorrect_credentials_returns_401_even_if_user_exists(self):
        resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "inactivo@test.com", "password": "ClaveEquivocada1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", resp.data)

    def test_login_exposes_is_superuser(self):
        # Login superusuario
        resp_super = self.client.post(
            "/api/usuarios/login/",
            {"email": "super_robust@test.com", "password": "SuperPassword1!"},
            format="json",
        )
        self.assertEqual(resp_super.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_super.data.get("is_superuser"))

        # Login usuario normal
        resp_normal = self.client.post(
            "/api/usuarios/login/",
            {"email": "activo@test.com", "password": "ActivoPassword1!"},
            format="json",
        )
        self.assertEqual(resp_normal.status_code, status.HTTP_200_OK)
        self.assertFalse(resp_normal.data.get("is_superuser"))

    def test_superadmin_cannot_self_deactivate(self):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "super_robust@test.com", "password": "SuperPassword1!"},
            format="json",
        )
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        resp = self.client.delete("/api/usuarios/me/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", resp.data)

        # Verificar que el superadmin sigue activo
        self.superadmin.refresh_from_db()
        self.assertTrue(self.superadmin.is_active)

    def test_regular_user_can_self_deactivate(self):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "activo@test.com", "password": "ActivoPassword1!"},
            format="json",
        )
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        resp = self.client.delete("/api/usuarios/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("mensaje", resp.data)

        self.usuario_activo.refresh_from_db()
        self.assertFalse(self.usuario_activo.is_active)

    def test_public_endpoints_ignore_invalid_or_expired_bearer_token(self):
        # Con token corrupto o expirado
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token_expirado_o_invalido_xyz")

        # 1. Login público
        resp_login = self.client.post(
            "/api/usuarios/login/",
            {"email": "activo@test.com", "password": "ActivoPassword1!"},
            format="json",
        )
        self.assertEqual(resp_login.status_code, status.HTTP_200_OK)

        # 2. Contacto público
        resp_contacto = self.client.post(
            "/api/usuarios/contacto/",
            {
                "email": "contacto@test.com",
                "asunto": "Consulta de prueba",
                "mensaje": "Mensaje de consulta",
            },
            format="json",
        )
        self.assertEqual(resp_contacto.status_code, status.HTTP_200_OK)

        # 3. Registro público
        resp_registro = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "Prueba Token Header",
                "email": "token_header@test.com",
                "dni": "77889900",
                "fdn": "1993-04-04",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_registro.status_code, status.HTTP_201_CREATED)

    def test_registro_dni_format_validations(self):
        self.client.credentials()

        # DNI con letras
        resp_letras = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "DNI Letras",
                "email": "dniletras@test.com",
                "dni": "1234ABCD",
                "fdn": "1990-01-01",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_letras.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp_letras.data)

        # DNI demasiado corto (6 dígitos)
        resp_corto = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "DNI Corto",
                "email": "dnicorto@test.com",
                "dni": "123456",
                "fdn": "1990-01-01",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_corto.status_code, status.HTTP_400_BAD_REQUEST)

        # DNI demasiado largo (9 dígitos)
        resp_largo = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "DNI Largo",
                "email": "dnilargo@test.com",
                "dni": "123456789",
                "fdn": "1990-01-01",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_largo.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_dni_and_email_uniqueness_returns_400_json_not_500(self):
        self.client.credentials()

        # DNI ya existente (pertenece a usuario_activo: 30303030)
        resp_dni_dup = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "Otro Nombre",
                "email": "nuevo_email@test.com",
                "dni": "30303030",
                "fdn": "1990-01-01",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_dni_dup.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp_dni_dup.data)

        # Email ya existente (pertenece a usuario_activo: activo@test.com)
        resp_email_dup = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "Otro Nombre",
                "email": "activo@test.com",
                "dni": "45678901",
                "fdn": "1990-01-01",
                "password": "PasswordValida1!",
            },
            format="json",
        )
        self.assertEqual(resp_email_dup.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp_email_dup.data)

    def test_contacto_requires_email(self):
        self.client.credentials()
        resp = self.client.post(
            "/api/usuarios/contacto/",
            {"asunto": "Consulta sin email", "mensaje": "Detalle de consulta"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.data)
        self.assertEqual(
            resp.data["error"], "El correo electrónico de contacto es obligatorio."
        )

    def test_admin_cannot_self_reset_password(self):
        login_resp = self.client.post(
            "/api/usuarios/login/",
            {"email": "super_robust@test.com", "password": "SuperPassword1!"},
            format="json",
        )
        token = login_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        resp = self.client.post(
            f"/api/usuarios/{self.superadmin.id}/reset-password/",
            {"nueva_password": "NuevaSuperClave1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", resp.data)
        self.assertIn("propia cuenta", resp.data["error"])


