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
