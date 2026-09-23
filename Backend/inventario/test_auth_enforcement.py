from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuario, Role
from .models import Producto, Sucursal, StockSucursal, Movimiento, Categoria


class AuthEnforcementAPITests(TestCase):
    """
    Suite de pruebas para verificar el enforcement global de autenticación en la API REST (ADR 0004).
    Principio: 'Seguro por defecto, público por excepción'.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        backend_dir = Path(__file__).resolve().parent.parent
        scripts = ["01_estructura.sql", "02_movimiento.sql", "03_datos.sql"]

        with connection.cursor() as cursor:
            for script_name in scripts:
                sql_path = backend_dir / "scripts" / script_name
                if sql_path.exists():
                    with open(sql_path, "r", encoding="utf-8") as f:
                        for stmt in f.read().split(";"):
                            stmt = stmt.strip()
                            if (
                                stmt
                                and not stmt.upper().startswith("DROP TABLE")
                                and not stmt.upper().startswith("CREATE DATABASE")
                                and not stmt.upper().startswith("USE ")
                            ):
                                try:
                                    cursor.execute(stmt)
                                except Exception:
                                    pass

    def setUp(self):
        self.client = APIClient()
        self.cat, _ = Categoria.objects.get_or_create(nombre="Categoría Test")
        self.producto, _ = Producto.objects.get_or_create(
            codigo="TEST-01",
            defaults={
                "nombre": "Producto Test Auth",
                "precio_venta": 1000.00,
                "stock_min_global": 10,
                "id_cat": self.cat,
            },
        )
        self.sucursal, _ = Sucursal.objects.get_or_create(
            nombre="Sucursal Test",
            defaults={"direccion": "Calle Test 123", "es_central": True},
        )
        if not self.sucursal.es_central:
            self.sucursal.es_central = True
            self.sucursal.save()
        self.stock, _ = StockSucursal.objects.get_or_create(
            id_art=self.producto,
            id_suc=self.sucursal,
            defaults={"cantidad_stock": 50, "stock_min": 10},
        )

        self.admin_user = Usuario.objects.create_superuser(
            nombre="Admin Auth Test",
            email="admintest@ejemplo.com",
            dni=99887766,
            fecha_nacimiento="1990-01-01",
            password="password123",
        )
        self.refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(self.refresh.access_token)

    # ---------------------------------------------------------
    # 1. Verificación de rechazo 401 para peticiones anónimas
    # ---------------------------------------------------------

    def test_anonymous_cannot_access_inventario_endpoints(self):
        endpoints = [
            "/api/inventario/productos/",
            "/api/inventario/categorias/",
            "/api/inventario/sucursales/",
            "/api/inventario/proveedores/",
            "/api/inventario/producto-proveedor/",
            "/api/inventario/stock/",
            "/api/inventario/movimientos/",
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"El endpoint {endpoint} debería rechazar peticiones anónimas con 401 Unauthorized",
            )

    def test_anonymous_cannot_access_vendedor_catalogo(self):
        response = self.client.get("/api/vendedor/productos/")
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "El catálogo de vendedor debe exigir autenticación.",
        )

    def test_anonymous_cannot_create_movimiento(self):
        payload = {
            "id_art": self.producto.id_art,
            "id_suc": self.sucursal.id_suc,
            "tipo": "Entrada",
            "cantidad": 5,
            "motivo": "Intento de entrada anónima",
        }
        response = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_bearer_token_returns_401(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token_completamente_invalido")
        response = self.client.get("/api/inventario/productos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------------------------------------
    # 2. Verificación de acceso a endpoints públicos de auth
    # ---------------------------------------------------------

    def test_public_login_endpoint_accessible_without_token(self):
        response = self.client.post(
            "/api/usuarios/login/",
            {"email": "admintest@ejemplo.com", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_public_registro_endpoint_accessible_without_token(self):
        response = self.client.post(
            "/api/usuarios/registro/",
            {
                "nombre": "Nuevo Usuario",
                "email": "nuevo@ejemplo.com",
                "dni": 11223344,
                "fdn": "1995-05-10",
                "password": "Password123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ---------------------------------------------------------
    # 3. Verificación de acceso permitido con JWT válido
    # ---------------------------------------------------------

    def test_authenticated_user_can_access_inventario_and_create_movimiento(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Consulta de productos
        response = self.client.get("/api/inventario/productos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Creación de movimiento con auditoría de usuario
        payload = {
            "id_art": self.producto.id_art,
            "id_suc": self.sucursal.id_suc,
            "tipo": "Entrada",
            "cantidad": 10,
            "motivo": "Ingreso autenticado",
        }
        res_mov = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(res_mov.status_code, status.HTTP_201_CREATED)

        # Verificar que el movimiento persistió id_usuario
        mov_id = res_mov.data.get("id_mov")
        mov_db = Movimiento.objects.get(id_mov=mov_id)
        self.assertEqual(mov_db.id_usuario, self.admin_user)
