# Backend/inventario/test_sucursales.py
import os
from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Sucursal, Categoria, Producto, StockSucursal, Movimiento


class SucursalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        backend_dir = Path(__file__).resolve().parent.parent
        estructura_sql = backend_dir / "scripts" / "01_estructura.sql"
        movimiento_sql = backend_dir / "scripts" / "02_movimiento.sql"

        with connection.cursor() as cursor:
            if estructura_sql.exists():
                with open(estructura_sql, "r", encoding="utf-8") as f:
                    for stmt in f.read().split(";"):
                        stmt = stmt.strip()
                        if stmt and not stmt.upper().startswith("DROP TABLE"):
                            try:
                                cursor.execute(stmt)
                            except Exception:
                                pass
            if movimiento_sql.exists():
                with open(movimiento_sql, "r", encoding="utf-8") as f:
                    for stmt in f.read().split(";"):
                        stmt = stmt.strip()
                        if stmt and not stmt.upper().startswith("DROP TABLE"):
                            try:
                                cursor.execute(stmt)
                            except Exception:
                                pass

    def setUp(self):
        self.client = APIClient()
        from usuarios.models import Usuario
        self.user, _ = Usuario.objects.get_or_create(
            email="admin_suc@ejemplo.com",
            defaults={
                "nombre": "Admin Suc",
                "dni": 12345672,
                "fecha_nacimiento": "1990-01-01",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.client.force_authenticate(user=self.user)
        self.categoria = Categoria.objects.create(nombre="Herramientas")
        self.producto = Producto.objects.create(
            nombre="Taladro Percutor",
            codigo="TAL-001",
            precio_venta=45000,
            id_cat=self.categoria,
        )

    def test_creacion_sucursal_y_auto_inicializacion(self):
        """Al crear una nueva sucursal, debe auto-inicializar StockSucursal en 0 para los productos existentes."""
        response = self.client.post(
            "/api/inventario/sucursales/",
            {"nombre": "Sede Centro", "direccion": "Av. Colón 1234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        suc_id = response.data["id_suc"]

        # Verificar que se creó StockSucursal
        stock = StockSucursal.objects.filter(id_suc_id=suc_id, id_art=self.producto)
        self.assertTrue(stock.exists())
        self.assertEqual(stock.first().cantidad_stock, 0)
        self.assertEqual(stock.first().stock_min, 0)

    def test_metricas_sucursal_en_serializer(self):
        """Verificar el cálculo de total_articulos, articulos_con_stock, articulos_sin_stock y articulos_alerta."""
        suc = Sucursal.objects.create(nombre="Sede Norte", direccion="Ruta 9 Km 10")
        StockSucursal.objects.filter(id_suc=suc).update(stock_min=0, cantidad_stock=0)
        stock = StockSucursal.objects.get(id_suc=suc, id_art=self.producto)
        stock.cantidad_stock = 5
        stock.stock_min = 10  # En alerta (5 <= 10)
        stock.save()

        total_prods = Producto.objects.count()
        response = self.client.get(f"/api/inventario/sucursales/{suc.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_articulos"], total_prods)
        self.assertEqual(response.data["articulos_con_stock"], 1)
        self.assertEqual(response.data["articulos_sin_stock"], total_prods - 1)
        self.assertEqual(response.data["articulos_alerta"], 1)

    def test_bloqueo_eliminacion_con_stock_activo(self):
        """No debe permitir eliminar una sucursal si tiene existencias físicas > 0."""
        suc = Sucursal.objects.create(nombre="Sede Sur", direccion="Av. Vélez Sársfield 500")
        stock = StockSucursal.objects.get(id_suc=suc, id_art=self.producto)
        stock.cantidad_stock = 15
        stock.save()

        response = self.client.delete(f"/api/inventario/sucursales/{suc.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("posee artículos con existencias de stock activas", response.data["error"])
        self.assertTrue(Sucursal.objects.filter(pk=suc.pk).exists())

    def test_bloqueo_eliminacion_con_movimientos(self):
        """No debe permitir eliminar una sucursal si tiene historial de movimientos."""
        suc = Sucursal.objects.create(nombre="Sede Este", direccion="Av. Sabattini 800")
        from django.utils import timezone
        Movimiento.objects.create(
            tipo="Entrada",
            cantidad=10,
            fecha_hora=timezone.now(),
            motivo="Compra inicial",
            id_art=self.producto,
            id_suc=suc,
        )

        response = self.client.delete(f"/api/inventario/sucursales/{suc.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cuenta con movimientos de inventario históricos", response.data["error"])

    def test_eliminacion_exitosa_sucursal_vacia(self):
        """Debe permitir eliminar una sucursal sin existencias activas ni movimientos."""
        suc = Sucursal.objects.create(nombre="Sede Temporal", direccion="Calle Falsa 123")
        response = self.client.delete(f"/api/inventario/sucursales/{suc.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sucursal.objects.filter(pk=suc.pk).exists())
        self.assertFalse(StockSucursal.objects.filter(id_suc_id=suc.pk).exists())

    def test_accion_inventario_por_sucursal(self):
        """El endpoint /sucursales/{id}/inventario/ debe listar los stocks de esa sede y filtrar por search."""
        suc = Sucursal.objects.create(nombre="Sede Oeste", direccion="Av. Fuerza Aérea 2000")
        suc.refresh_from_db()
        StockSucursal.objects.get_or_create(
            id_art=self.producto, id_suc=suc, defaults={"cantidad_stock": 20, "stock_min": 5}
        )

        url = f"/api/inventario/sucursales/{suc.id_suc}/inventario/"
        response = self.client.get(url, data={"search": "Taladro"})
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Fallo en {url}: {response.content.decode('utf-8') if hasattr(response, 'content') else response}",
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre_producto"], "Taladro Percutor")

    def test_bloqueo_eliminacion_casa_central(self):
        """No debe permitir eliminar una sucursal si está designada como Casa Central."""
        suc_central = Sucursal.objects.create(nombre="Sede Central Test", direccion="Av. Central 1", es_central=True)
        response = self.client.delete(f"/api/inventario/sucursales/{suc_central.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("designada como Casa Central", response.data["error"])
        self.assertTrue(Sucursal.objects.filter(pk=suc_central.pk).exists())

    def test_auto_promocion_y_unicidad_casa_central(self):
        """La primera sede creada debe auto-promoverse a central, y promover una nueva debe desmarcar la anterior."""
        Sucursal.objects.filter(es_central=True).update(es_central=False)
        res1 = self.client.post("/api/inventario/sucursales/", {"nombre": "Primera Sede Test", "direccion": "Dir 1"})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res1.data["es_central"])

        res2 = self.client.post("/api/inventario/sucursales/", {"nombre": "Segunda Sede", "direccion": "Dir 2", "es_central": True})
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res2.data["es_central"])

        # La primera debe haber sido desmarcada
        s1 = Sucursal.objects.get(pk=res1.data["id_suc"])
        self.assertFalse(s1.es_central)

    def test_bloqueo_entrada_proveedor_en_sucursal_no_central(self):
        """Las compras a proveedores (Entrada) no deben permitirse en sucursales secundarias."""
        suc_secundaria = Sucursal.objects.create(nombre="Sucursal Satelite", direccion="Calle Satelite 12", es_central=False)
        payload = {
            "id_art": self.producto.id_art,
            "id_suc": suc_secundaria.id_suc,
            "tipo": "Entrada",
            "cantidad": 10,
            "motivo": "Compra directa indebida",
        }
        response = self.client.post("/api/inventario/movimientos/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("solo pueden recibirse en la Casa Central", response.data["error"])
