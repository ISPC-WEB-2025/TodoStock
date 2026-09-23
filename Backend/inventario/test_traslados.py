from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Producto, Sucursal, StockSucursal, Movimiento


class TrasladosRegistroDualAPITests(TestCase):
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
        from usuarios.models import Usuario
        self.user, _ = Usuario.objects.get_or_create(
            email="admin_tras@ejemplo.com",
            defaults={
                "nombre": "Admin Traslados",
                "dni": 12345673,
                "fecha_nacimiento": "1990-01-01",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.client.force_authenticate(user=self.user)
        from .models import Categoria
        self.cat, _ = Categoria.objects.get_or_create(nombre="Perfiles de aluminio")
        self.producto, _ = Producto.objects.get_or_create(
            codigo="ALU-45",
            defaults={
                "nombre": "Perfil de aluminio 45mm",
                "precio_venta": 12500.00,
                "stock_min_global": 50,
                "id_cat": self.cat,
            },
        )
        self.suc_origen, _ = Sucursal.objects.get_or_create(
            nombre="Fábrica Principal",
            defaults={"direccion": "Calle Industrial 100"},
        )
        self.suc_destino, _ = Sucursal.objects.get_or_create(
            nombre="Depósito Zona Sur",
            defaults={"direccion": "Av. Sabattini 3200"},
        )

        # Asegurar existencias conocidas
        self.stock_origen, _ = StockSucursal.objects.get_or_create(
            id_art=self.producto,
            id_suc=self.suc_origen,
            defaults={"cantidad_stock": 100, "stock_min": 50},
        )
        self.stock_origen.cantidad_stock = 100
        self.stock_origen.save()

        self.stock_destino, _ = StockSucursal.objects.get_or_create(
            id_art=self.producto,
            id_suc=self.suc_destino,
            defaults={"cantidad_stock": 20, "stock_min": 5},
        )
        self.stock_destino.cantidad_stock = 20
        self.stock_destino.save()

    def test_traslado_genera_dos_movimientos_y_actualiza_stocks(self):
        """Verifica que un traslado cree dos registros simétricos y debite/acredite existencias."""
        total_movs_antes = Movimiento.objects.count()

        payload = {
            "tipo": "Traslado",
            "id_art": self.producto.id_art,
            "id_suc": self.suc_origen.id_suc,
            "id_suc_destino": self.suc_destino.id_suc,
            "cantidad": 15,
            "motivo": "Rebalanceo de stock",
        }

        response = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 1. Verificar actualización de existencias en base de datos
        self.stock_origen.refresh_from_db()
        self.stock_destino.refresh_from_db()
        self.assertEqual(self.stock_origen.cantidad_stock, 85)
        self.assertEqual(self.stock_destino.cantidad_stock, 35)

        # 2. Verificar que se hayan creado 2 movimientos
        total_movs_despues = Movimiento.objects.count()
        self.assertEqual(total_movs_despues, total_movs_antes + 2)

        # 3. Verificar movimiento de egreso en origen
        mov_egreso = Movimiento.objects.filter(
            id_art=self.producto,
            id_suc=self.suc_origen,
            tipo="Traslado",
            cantidad=15,
        ).latest("id_mov")
        self.assertEqual(mov_egreso.stock_previo, 100)
        self.assertIn("Traslado hacia", mov_egreso.motivo)
        self.assertIn("Depósito Zona Sur", mov_egreso.motivo)

        # 4. Verificar movimiento de ingreso en destino
        mov_ingreso = Movimiento.objects.filter(
            id_art=self.producto,
            id_suc=self.suc_destino,
            tipo="Traslado",
            cantidad=15,
        ).latest("id_mov")
        self.assertEqual(mov_ingreso.stock_previo, 20)
        self.assertIn("Recepción desde", mov_ingreso.motivo)
        self.assertIn("Fábrica Principal", mov_ingreso.motivo)

    def test_filtrado_server_side_muestra_movimiento_a_cada_sucursal(self):
        """Verifica que el filtrado ?id_suc=X retorne el traslado tanto al origen como al destino."""
        payload = {
            "tipo": "Traslado",
            "id_art": self.producto.id_art,
            "id_suc": self.suc_origen.id_suc,
            "id_suc_destino": self.suc_destino.id_suc,
            "cantidad": 10,
        }
        resp_post = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)

        # Origen ve su egreso
        resp_origen = self.client.get(f"/api/inventario/movimientos/?id_suc={self.suc_origen.id_suc}")
        self.assertEqual(resp_origen.status_code, status.HTTP_200_OK)
        motivos_origen = [m["motivo"] for m in resp_origen.data]
        self.assertTrue(any("Traslado hacia" in (m or "") for m in motivos_origen))

        # Destino ve su recepción
        resp_destino = self.client.get(f"/api/inventario/movimientos/?id_suc={self.suc_destino.id_suc}")
        self.assertEqual(resp_destino.status_code, status.HTTP_200_OK)
        motivos_destino = [m["motivo"] for m in resp_destino.data]
        self.assertTrue(any("Recepción desde" in (m or "") for m in motivos_destino))

    def test_traslado_falla_por_stock_insuficiente(self):
        """Verifica que no se generen movimientos ni cambios de stock si la cantidad supera el disponible."""
        total_movs_antes = Movimiento.objects.count()

        payload = {
            "tipo": "Traslado",
            "id_art": self.producto.id_art,
            "id_suc": self.suc_origen.id_suc,
            "id_suc_destino": self.suc_destino.id_suc,
            "cantidad": 9999,
        }
        response = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Stock insuficiente", response.data.get("error", ""))

        self.stock_origen.refresh_from_db()
        self.stock_destino.refresh_from_db()
        self.assertEqual(self.stock_origen.cantidad_stock, 100)
        self.assertEqual(self.stock_destino.cantidad_stock, 20)
        self.assertEqual(Movimiento.objects.count(), total_movs_antes)
