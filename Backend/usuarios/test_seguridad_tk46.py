from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from usuarios.models import Usuario


class SeguridadTK46Tests(TestCase):
    """TK46: CORS restringido, ALLOWED_HOSTS sin comodín y bloqueo por intentos fallidos de login."""

    def setUp(self):
        self.client = APIClient()
        Usuario.objects.create_user(
            email="tk46@test.com",
            nombre="Usuario TK46",
            dni="46464646",
            fecha_nacimiento="1995-05-05",
            password="ClaveCorrecta123!",
        )

    def _login(self, password):
        return self.client.post(
            "/api/usuarios/login/",
            {"email": "tk46@test.com", "password": password},
            format="json",
        )

    @override_settings(AXES_FAILURE_LIMIT=3)
    def test_login_se_bloquea_al_llegar_al_limite_de_intentos_fallidos(self):
        self.assertEqual(self._login("incorrecta").status_code, 401)
        self.assertEqual(self._login("incorrecta").status_code, 401)
        self.assertEqual(self._login("incorrecta").status_code, 429)
        # Mientras dura el bloqueo, ni siquiera la contraseña correcta permite entrar.
        self.assertEqual(self._login("ClaveCorrecta123!").status_code, 429)

    @override_settings(AXES_FAILURE_LIMIT=3)
    def test_login_correcto_no_se_bloquea(self):
        self.assertEqual(self._login("ClaveCorrecta123!").status_code, 200)

    def test_cors_rechaza_origen_no_autorizado(self):
        respuesta = self.client.options(
            "/api/usuarios/login/",
            HTTP_ORIGIN="https://sitio-malicioso.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertNotIn("access-control-allow-origin", respuesta.headers)

    def test_cors_acepta_origen_del_frontend(self):
        respuesta = self.client.options(
            "/api/usuarios/login/",
            HTTP_ORIGIN="http://localhost:4200",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertEqual(respuesta.headers.get("access-control-allow-origin"), "http://localhost:4200")

    def test_host_no_listado_es_rechazado(self):
        respuesta = self.client.post(
            "/api/usuarios/login/",
            {"email": "tk46@test.com", "password": "x"},
            format="json",
            HTTP_HOST="atacante.com",
        )
        self.assertEqual(respuesta.status_code, 400)
