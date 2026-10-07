from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Producto, Sucursal, Movimiento
from usuarios.models import Usuario


class MobileAPIReadinessTests(TestCase):
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
        from .models import Categoria
        self.user, _ = Usuario.objects.get_or_create(
            email="admin_mobile@ejemplo.com",
            defaults={
                "nombre": "Admin Mobile",
                "dni": 12345675,
                "fecha_nacimiento": "1990-01-01",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.client.force_authenticate(user=self.user)

        self.cat_alum, _ = Categoria.objects.get_or_create(nombre="Perfiles de aluminio")
        self.cat_motores, _ = Categoria.objects.get_or_create(nombre="Motores")

        from usuarios.models import Role
        self.role_emp, _ = Role.objects.get_or_create(nombre="EMPLEADO")
        self.empleado_user, _ = Usuario.objects.get_or_create(
            email="empleado_mobile@ejemplo.com",
            defaults={
                "nombre": "Empleado Mobile",
                "dni": 44556677,
                "fecha_nacimiento": "1994-04-04",
                "rol": self.role_emp,
                "is_staff": False,
                "is_superuser": False,
            },
        )

        self.prod_perfil, _ = Producto.objects.get_or_create(
            codigo="ALU-45",
            defaults={
                "nombre": "Perfil de aluminio 45mm",
                "precio_venta": 12500.00,
                "id_cat": self.cat_alum,
                "stock_min_global": 50,
            },
        )
        self.prod_motor, _ = Producto.objects.get_or_create(
            codigo="MOT-50",
            defaults={
                "nombre": "Motor Tubular 50Nm",
                "precio_venta": 85000.00,
                "id_cat": self.cat_motores,
                "stock_min_global": 5,
            },
        )
        self.suc_fabrica, _ = Sucursal.objects.get_or_create(
            nombre="Fábrica Principal",
            defaults={"direccion": "Calle Industrial 100", "es_central": True},
        )
        self.suc_secundaria, _ = Sucursal.objects.get_or_create(
            nombre="Sucursal Centro",
            defaults={"direccion": "Av. Colón 500", "es_central": False},
        )

    def test_busqueda_exacta_codigo_para_escaner(self):
        """Verifica que ?codigo= retorne exclusivamente el producto escaneado."""
        response = self.client.get(f"/api/inventario/productos/?codigo={self.prod_perfil.codigo}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["codigo"], "ALU-45")
        self.assertEqual(response.data[0]["nombre"], self.prod_perfil.nombre)

    def test_busqueda_codigo_case_insensitive(self):
        """Verifica que el escaneo funcione aún con variaciones de minúsculas/mayúsculas."""
        response = self.client.get("/api/inventario/productos/?codigo=alu-45")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["codigo"], "ALU-45")

    def test_filtro_productos_por_categoria(self):
        """Verifica que ?id_cat= filtre los productos de dicha categoría."""
        id_cat = self.prod_perfil.id_cat.id_cat
        response = self.client.get(f"/api/inventario/productos/?id_cat={id_cat}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["id_cat"] == id_cat for p in response.data))

    def test_filtro_movimientos_por_sucursal_y_tipo(self):
        """Verifica que /api/inventario/movimientos/ permita filtrar por tipo y sucursal."""
        from django.utils import timezone
        # Registrar un movimiento de salida
        mov = Movimiento.objects.create(
            tipo="Salida",
            cantidad=2,
            id_art=self.prod_perfil,
            id_suc=self.suc_fabrica,
            fecha_hora=timezone.now(),
            motivo="Venta Mostrador App Móvil",
        )

        resp = self.client.get(
            f"/api/inventario/movimientos/?id_suc={self.suc_fabrica.id_suc}&tipo=Salida"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(all(m["tipo"] == "Salida" for m in resp.data))
        self.assertTrue(all(m["id_suc"] == self.suc_fabrica.id_suc for m in resp.data))

    def test_endpoint_perfil_usuario_me(self):
        """Verifica que /api/usuarios/me/ retorne los datos del usuario autenticado."""
        # Obtener un usuario existente de la base de datos
        user = Usuario.objects.first()
        if user:
            self.client.force_authenticate(user=user)
            response = self.client.get("/api/usuarios/me/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["email"], user.email)
            self.assertIn("es_admin", response.data)
            self.assertIn("es_empleado", response.data)

    def test_empleado_cannot_mutate_products(self):
        """Verifica que un empleado reciba 403 al intentar crear o eliminar productos (US05, US09)."""
        self.client.force_authenticate(user=self.empleado_user)

        # Intento de creación
        resp_post = self.client.post(
            "/api/inventario/productos/",
            {
                "codigo": "NO-AUTH-1",
                "nombre": "Producto No Autorizado",
                "precio_venta": 500.0,
                "stock_min_global": 10,
            },
            format="json",
        )
        self.assertEqual(resp_post.status_code, status.HTTP_403_FORBIDDEN)

        # Intento de eliminación
        resp_del = self.client.delete(f"/api/inventario/productos/{self.prod_perfil.id_art}/")
        self.assertEqual(resp_del.status_code, status.HTTP_403_FORBIDDEN)

    def test_empleado_can_read_products_and_branch_inventory(self):
        """Verifica que un empleado pueda listar catálogo y consultar stock por sucursal (US03)."""
        self.client.force_authenticate(user=self.empleado_user)

        # Listar catálogo
        resp_list = self.client.get("/api/inventario/productos/")
        self.assertEqual(resp_list.status_code, status.HTTP_200_OK)

        # Consultar stock por sucursal
        resp_stock = self.client.get(f"/api/inventario/sucursales/{self.suc_fabrica.id_suc}/inventario/")
        self.assertEqual(resp_stock.status_code, status.HTTP_200_OK)

    def test_empleado_can_transfer_but_cannot_register_entrada(self):
        """Verifica que un empleado pueda registrar traslados (US06) pero no compras/entradas."""
        from .models import StockSucursal
        # Crear stock previo en origen
        StockSucursal.objects.update_or_create(
            id_art=self.prod_perfil,
            id_suc=self.suc_fabrica,
            defaults={"cantidad_stock": 20, "stock_min": 5},
        )
        StockSucursal.objects.update_or_create(
            id_art=self.prod_perfil,
            id_suc=self.suc_secundaria,
            defaults={"cantidad_stock": 0, "stock_min": 2},
        )

        self.client.force_authenticate(user=self.empleado_user)

        # Intento de Entrada a compras -> 403 Forbidden
        resp_entrada = self.client.post(
            "/api/inventario/movimientos/",
            {
                "tipo": "Entrada",
                "cantidad": 10,
                "id_art": self.prod_perfil.id_art,
                "id_suc": self.suc_fabrica.id_suc,
            },
            format="json",
        )
        self.assertEqual(resp_entrada.status_code, status.HTTP_403_FORBIDDEN)

        # Registro de Traslado -> 201 Created
        resp_traslado = self.client.post(
            "/api/inventario/movimientos/",
            {
                "tipo": "Traslado",
                "cantidad": 5,
                "id_art": self.prod_perfil.id_art,
                "id_suc": self.suc_fabrica.id_suc,
                "id_suc_destino": self.suc_secundaria.id_suc,
                "motivo": "Reabastecimiento sucursal centro",
            },
            format="json",
        )
        self.assertEqual(resp_traslado.status_code, status.HTTP_201_CREATED)

