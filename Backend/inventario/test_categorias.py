# Backend/inventario/test_categorias.py
from pathlib import Path
from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from .models import Categoria, Producto


class CategoriaTests(TestCase):
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
            email="admin_cat@ejemplo.com",
            defaults={
                "nombre": "Admin Cat",
                "dni": 12345671,
                "fecha_nacimiento": "1990-01-01",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.client.force_authenticate(user=self.user)
        self.cat_herramientas = Categoria.objects.create(nombre="Herramientas")
        self.cat_iluminacion = Categoria.objects.create(nombre="Iluminación")

        self.prod1 = Producto.objects.create(
            nombre="Taladro Percutor 750W",
            codigo="TAL-001",
            precio_venta=45000,
            id_cat=self.cat_herramientas,
        )
        self.prod2 = Producto.objects.create(
            nombre="Amoladora Angular 115mm",
            codigo="AMO-002",
            precio_venta=38000,
            id_cat=self.cat_herramientas,
        )

    def test_creacion_categoria_exitosa(self):
        """Debe permitir crear una nueva categoría con nombre válido."""
        response = self.client.post(
            "/api/inventario/categorias/",
            {"nombre": "Pinturas y Adhesivos"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Pinturas y Adhesivos")
        self.assertEqual(response.data["total_articulos"], 0)

    def test_validacion_nombre_unico_case_insensitive(self):
        """Debe rechazar la creación de una categoría si el nombre ya existe (sin importar mayúsculas/minúsculas)."""
        response = self.client.post(
            "/api/inventario/categorias/",
            {"nombre": "herramientas"},  # Ya existe "Herramientas"
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ya existe una categoría con el nombre", str(response.data))

    def test_validacion_nombre_vacio(self):
        """Debe rechazar nombres vacíos o que solo contengan espacios."""
        response = self.client.post(
            "/api/inventario/categorias/",
            {"nombre": "   "},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_metrica_total_articulos(self):
        """El serializer debe calcular correctamente la cantidad de productos asociados."""
        response = self.client.get(f"/api/inventario/categorias/{self.cat_herramientas.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_articulos"], 2)

        response_ilum = self.client.get(f"/api/inventario/categorias/{self.cat_iluminacion.pk}/")
        self.assertEqual(response_ilum.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ilum.data["total_articulos"], 0)

    def test_accion_productos_por_categoria(self):
        """El endpoint /categorias/{id}/productos/ debe listar los artículos pertenecientes a esa categoría."""
        response = self.client.get(f"/api/inventario/categorias/{self.cat_herramientas.pk}/productos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        codigos = [p["codigo"] for p in response.data]
        self.assertIn("TAL-001", codigos)
        self.assertIn("AMO-002", codigos)

    def test_accion_productos_por_categoria_con_filtro_busqueda(self):
        """El endpoint /categorias/{id}/productos/?search=... debe filtrar por nombre o código."""
        response = self.client.get(
            f"/api/inventario/categorias/{self.cat_herramientas.pk}/productos/?search=Taladro"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["codigo"], "TAL-001")

    def test_bloqueo_eliminacion_con_productos_asociados(self):
        """No debe permitir eliminar una categoría si tiene productos asociados (HTTP 400)."""
        response = self.client.delete(f"/api/inventario/categorias/{self.cat_herramientas.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("posee 2 producto(s) asociado(s)", response.data["error"])
        self.assertTrue(Categoria.objects.filter(pk=self.cat_herramientas.pk).exists())

    def test_eliminacion_exitosa_sin_productos(self):
        """Debe permitir eliminar una categoría si no tiene productos asociados (HTTP 204)."""
        response = self.client.delete(f"/api/inventario/categorias/{self.cat_iluminacion.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Categoria.objects.filter(pk=self.cat_iluminacion.pk).exists())

    def test_actualizacion_categoria_valida_e_invalida(self):
        """Permite renombrar una categoría a un nombre libre, pero bloquea si choca con otra categoría existente."""
        # Actualización válida
        response = self.client.put(
            f"/api/inventario/categorias/{self.cat_iluminacion.pk}/",
            {"nombre": "Iluminación LED y Solar"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat_iluminacion.refresh_from_db()
        self.assertEqual(self.cat_iluminacion.nombre, "Iluminación LED y Solar")

        # Actualización con conflicto
        response_conflict = self.client.put(
            f"/api/inventario/categorias/{self.cat_iluminacion.pk}/",
            {"nombre": "HERRAMIENTAS"},
            format="json",
        )
        self.assertEqual(response_conflict.status_code, status.HTTP_400_BAD_REQUEST)
