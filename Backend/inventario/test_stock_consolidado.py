from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Producto, Sucursal, StockSucursal


class StockConsolidadoAPITests(TestCase):
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
                            if stmt and not stmt.upper().startswith("DROP TABLE") and not stmt.upper().startswith("CREATE DATABASE") and not stmt.upper().startswith("USE "):
                                try:
                                    cursor.execute(stmt)
                                except Exception:
                                    pass

    def setUp(self):
        self.client = APIClient()
        from usuarios.models import Usuario
        from .models import Categoria
        self.user, _ = Usuario.objects.get_or_create(
            email="admin_stock@ejemplo.com",
            defaults={
                "nombre": "Admin Stock",
                "dni": 12345674,
                "fecha_nacimiento": "1990-01-01",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.client.force_authenticate(user=self.user)

        self.cat_alum, _ = Categoria.objects.get_or_create(nombre="Perfiles de aluminio")
        self.cat_motores, _ = Categoria.objects.get_or_create(nombre="Motores")

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
            defaults={"direccion": "Calle Industrial 100"},
        )
        self.suc_deposito, _ = Sucursal.objects.get_or_create(
            nombre="Depósito Zona Sur",
            defaults={"direccion": "Av. Sabattini 3200"},
        )

        st1, _ = StockSucursal.objects.get_or_create(
            id_art=self.prod_perfil,
            id_suc=self.suc_fabrica,
            defaults={"cantidad_stock": 100, "stock_min": 50},
        )
        st1.cantidad_stock = 100
        st1.save()

        st2, _ = StockSucursal.objects.get_or_create(
            id_art=self.prod_perfil,
            id_suc=self.suc_deposito,
            defaults={"cantidad_stock": 50, "stock_min": 20},
        )
        st2.cantidad_stock = 50
        st2.save()

        st3, _ = StockSucursal.objects.get_or_create(
            id_art=self.prod_motor,
            id_suc=self.suc_fabrica,
            defaults={"cantidad_stock": 20, "stock_min": 5},
        )
        st3.cantidad_stock = 20
        st3.save()

    def test_stock_total_consolidado_en_producto(self):
        """Verifica que /api/inventario/productos/{id}/ retorne el stock_total sumado en la red."""
        response = self.client.get(f"/api/inventario/productos/{self.prod_perfil.id_art}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["codigo"], "ALU-45")
        self.assertEqual(response.data["stock_total"], 150)

    def test_endpoint_producto_stock_desglose(self):
        """Verifica que /api/inventario/productos/{id}/stock/ retorne el desglose por sucursal."""
        response = self.client.get(f"/api/inventario/productos/{self.prod_perfil.id_art}/stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
        nombres = [item["nombre_sucursal"] for item in response.data]
        self.assertIn("Fábrica Principal", nombres)
        self.assertIn("Depósito Zona Sur", nombres)

    def test_filtro_stock_sucursal_por_query_params(self):
        """Verifica que /api/inventario/stock/ permita filtrar por id_art e id_suc."""
        resp_art = self.client.get(f"/api/inventario/stock/?id_art={self.prod_motor.id_art}")
        self.assertEqual(resp_art.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["id_art"] == self.prod_motor.id_art for item in resp_art.data))

        resp_suc = self.client.get(f"/api/inventario/stock/?id_suc={self.suc_fabrica.id_suc}")
        self.assertEqual(resp_suc.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["id_suc"] == self.suc_fabrica.id_suc for item in resp_suc.data))

    def test_filtro_solo_con_stock_en_sucursal_inventario(self):
        """Verifica que /api/inventario/sucursales/{id}/inventario/?solo_con_stock=true filtre items en 0."""
        resp_filtrado = self.client.get(
            f"/api/inventario/sucursales/{self.suc_fabrica.id_suc}/inventario/?solo_con_stock=true"
        )
        self.assertEqual(resp_filtrado.status_code, status.HTTP_200_OK)
        for item in resp_filtrado.data:
            self.assertGreater(item["cantidad_stock"], 0)

    def test_validacion_stock_min_global_negativo(self):
        """Verifica que la API rechace stock_min_global negativo en el producto."""
        payload = {
            "nombre": "Producto Inválido",
            "codigo": "PROD-INV-01",
            "precio_venta": "1000.00",
            "stock_min_global": -10,
            "id_cat": self.prod_perfil.id_cat.id_cat,
        }
        response = self.client.post("/api/inventario/productos/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        detalles = response.data.get("detalle", response.data)
        self.assertIn("stock_min_global", detalles)
