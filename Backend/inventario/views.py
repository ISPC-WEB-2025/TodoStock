from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models, transaction
from .models import (
    Producto,
    Categoria,
    Sucursal,
    Proveedor,
    ProductoProveedor,
    StockSucursal,
    Movimiento,
)
from .serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    SucursalSerializer,
    ProveedorSerializer,
    ProductoProveedorSerializer,
    StockSucursalSerializer,
    MovimientoSerializer,
)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "codigo"]
    ordering_fields = ["id_art", "nombre", "codigo", "precio_venta", "stock_min_global"]

    def get_queryset(self):
        queryset = super().get_queryset()
        codigo = self.request.query_params.get("codigo")
        if codigo:
            queryset = queryset.filter(codigo__iexact=codigo.strip())
        id_cat = self.request.query_params.get("id_cat") or self.request.query_params.get("categoria")
        if id_cat:
            queryset = queryset.filter(id_cat_id=id_cat)
        return queryset

    @action(detail=True, methods=["get"], url_path="stock", filter_backends=[])
    def stock(self, request, pk=None):
        producto = self.get_object()
        stock_qs = StockSucursal.objects.select_related("id_art", "id_suc").filter(
            id_art=producto
        )
        serializer = StockSucursalSerializer(stock_qs, many=True)
        return Response(serializer.data)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["id_cat", "nombre"]

    def destroy(self, request, *args, **kwargs):
        categoria = self.get_object()
        articulos_count = Producto.objects.filter(id_cat=categoria).count()
        if articulos_count > 0:
            return Response(
                {
                    "error": f"No se puede eliminar la categoría '{categoria.nombre}' porque posee {articulos_count} producto(s) asociado(s)."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        categoria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="productos", filter_backends=[])
    def productos(self, request, pk=None):
        categoria = self.get_object()
        prods_qs = Producto.objects.filter(id_cat=categoria)
        query = request.query_params.get("search", None)
        if query:
            prods_qs = prods_qs.filter(
                models.Q(nombre__icontains=query) | models.Q(codigo__icontains=query)
            )
        serializer = ProductoSerializer(prods_qs, many=True)
        return Response(serializer.data)


class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "direccion"]
    ordering_fields = ["id_suc", "nombre", "direccion"]

    def destroy(self, request, *args, **kwargs):
        sucursal = self.get_object()

        # Validar si es la Casa Central activa del sistema
        if sucursal.es_central:
            return Response(
                {
                    "error": f"No se puede eliminar la sucursal '{sucursal.nombre}' porque está designada como Casa Central del sistema. Para darla de baja, primero debe designar otra sucursal como Central."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar si tiene stock físico activo mayor a 0
        tiene_stock_activo = StockSucursal.objects.filter(
            id_suc=sucursal, cantidad_stock__gt=0
        ).exists()
        if tiene_stock_activo:
            return Response(
                {
                    "error": f"No se puede eliminar la sucursal '{sucursal.nombre}' porque posee artículos con existencias de stock activas."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar si tiene movimientos históricos registrados
        tiene_movimientos = Movimiento.objects.filter(id_suc=sucursal).exists()
        if tiene_movimientos:
            return Response(
                {
                    "error": f"No se puede eliminar la sucursal '{sucursal.nombre}' porque cuenta con movimientos de inventario históricos registrados."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Si está limpia (solo tiene registros de stock en 0 y sin movimientos),
        # eliminar registros vinculados de StockSucursal en bloque atómico y la sucursal
        with transaction.atomic():
            StockSucursal.objects.filter(id_suc=sucursal).delete()
            sucursal.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="inventario", filter_backends=[])
    def inventario(self, request, pk=None):
        sucursal = self.get_queryset().get(pk=pk)
        stock_qs = StockSucursal.objects.select_related("id_art", "id_suc").filter(
            id_suc=sucursal
        )

        solo_con_stock = request.query_params.get("solo_con_stock", None)
        if solo_con_stock and solo_con_stock.lower() in ["true", "1", "yes"]:
            stock_qs = stock_qs.filter(cantidad_stock__gt=0)

        query = request.query_params.get("search", None)
        if query:
            stock_qs = stock_qs.filter(
                models.Q(id_art__nombre__icontains=query)
                | models.Q(id_art__codigo__icontains=query)
            )

        serializer = StockSucursalSerializer(stock_qs, many=True)
        return Response(serializer.data)


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "cuit", "email"]
    ordering_fields = ["id_prov", "nombre", "cuit"]


class ProductoProveedorViewSet(viewsets.ModelViewSet):
    queryset = ProductoProveedor.objects.select_related("id_art", "id_prov").all()
    serializer_class = ProductoProveedorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["id_art__nombre", "id_prov__nombre"]


class StockSucursalViewSet(viewsets.ModelViewSet):
    serializer_class = StockSucursalSerializer

    def get_queryset(self):
        queryset = StockSucursal.objects.select_related("id_art", "id_suc").all()
        id_art = self.request.query_params.get("id_art")
        if id_art:
            queryset = queryset.filter(id_art_id=id_art)
        id_suc = self.request.query_params.get("id_suc")
        if id_suc:
            queryset = queryset.filter(id_suc_id=id_suc)
        return queryset

    # REMOVIDO: update()
    # Justificación: Redundante. El método update() nativo de ModelViewSet ya procesa
    # internamente la actualización y retorna un estado HTTP 200 OK por defecto.
    # Forzar el status_code manualmente no altera ni aporta comportamiento extra.

    # REMOVIDO: destroy()
    # Justificación: Código muerto (Dead Code). Invocar a super().destroy() sin añadir
    # lógica de validación previa o posterior al borrado duplica el comportamiento
    # heredado de la clase padre sin ningún propósito técnico


class MovimientoViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["id_mov", "fecha_hora", "cantidad"]

    def get_queryset(self):
        queryset = Movimiento.objects.select_related("id_art", "id_suc", "id_prov").all()
        id_art = self.request.query_params.get("id_art")
        if id_art:
            queryset = queryset.filter(id_art_id=id_art)
        id_suc = self.request.query_params.get("id_suc")
        if id_suc:
            queryset = queryset.filter(id_suc_id=id_suc)
        tipo = self.request.query_params.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo__iexact=tipo.strip())
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tipo = serializer.validated_data["tipo"]
        cantidad = serializer.validated_data["cantidad"]
        producto = serializer.validated_data["id_art"]
        sucursal = serializer.validated_data["id_suc"]
        sucursal_destino = serializer.validated_data.get("id_suc_destino")

        # Asignar usuario autenticado si no fue provisto
        if request.user and request.user.is_authenticated and not serializer.validated_data.get("id_usuario"):
            serializer.validated_data["id_usuario"] = request.user

        # Validar permisos y sede central para Entradas
        if tipo == "Entrada":
            es_admin = getattr(request.user, "es_admin", False) or getattr(request.user, "is_superuser", False)
            if request.user.is_authenticated and not es_admin:
                return Response(
                    {"error": "Los vendedores no pueden registrar entradas de stock."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not getattr(sucursal, "es_central", False):
                return Response(
                    {
                        "error": f"Las compras a proveedores solo pueden recibirse en la Casa Central / Fábrica Principal. La sede '{sucursal.nombre}' es una sucursal secundaria."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validaciones para Traslados
        if tipo == "Traslado":
            if not sucursal_destino:
                return Response(
                    {"error": "Debe especificar la sucursal de destino para el traslado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if sucursal_destino.pk == sucursal.pk:
                return Response(
                    {"error": "La sucursal de origen y destino no pueden ser la misma."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            if tipo == "Entrada":
                stock_obj, _ = StockSucursal.objects.select_for_update().get_or_create(
                    id_art=producto,
                    id_suc=sucursal,
                    defaults={"cantidad_stock": 0, "stock_min": 0},
                )
                serializer.validated_data["stock_previo"] = stock_obj.cantidad_stock
                stock_obj.cantidad_stock += cantidad
                stock_obj.save()

            elif tipo == "Salida":
                stock_obj = (
                    StockSucursal.objects.select_for_update()
                    .filter(id_art=producto, id_suc=sucursal)
                    .first()
                )
                if not stock_obj:
                    return Response(
                        {"error": "No existe registro de stock para ese producto en esa sucursal."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if stock_obj.cantidad_stock < cantidad:
                    return Response(
                        {
                            "error": "Stock insuficiente.",
                            "stock_disponible": stock_obj.cantidad_stock,
                            "cantidad_solicitada": cantidad,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer.validated_data["stock_previo"] = stock_obj.cantidad_stock
                stock_obj.cantidad_stock -= cantidad
                stock_obj.save()

            elif tipo == "Traslado":
                stock_origen = (
                    StockSucursal.objects.select_for_update()
                    .filter(id_art=producto, id_suc=sucursal)
                    .first()
                )
                if not stock_origen:
                    return Response(
                        {"error": "No existe registro de stock en la sucursal de origen."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if stock_origen.cantidad_stock < cantidad:
                    return Response(
                        {
                            "error": "Stock insuficiente en la sucursal de origen.",
                            "stock_disponible": stock_origen.cantidad_stock,
                            "cantidad_solicitada": cantidad,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                stock_destino, _ = StockSucursal.objects.select_for_update().get_or_create(
                    id_art=producto,
                    id_suc=sucursal_destino,
                    defaults={"cantidad_stock": 0, "stock_min": producto.stock_min_global},
                )

                stock_previo_origen = stock_origen.cantidad_stock
                stock_previo_destino = stock_destino.cantidad_stock

                stock_origen.cantidad_stock -= cantidad
                stock_destino.cantidad_stock += cantidad

                stock_origen.save()
                stock_destino.save()

                motivo_custom = serializer.validated_data.get("motivo")
                if motivo_custom and motivo_custom.strip():
                    serializer.validated_data["motivo"] = (
                        f"Traslado hacia {sucursal_destino.nombre} ({motivo_custom.strip()})"
                    )
                    motivo_destino = f"Recepción desde {sucursal.nombre} ({motivo_custom.strip()})"
                else:
                    serializer.validated_data["motivo"] = f"Traslado hacia {sucursal_destino.nombre}"
                    motivo_destino = f"Recepción desde {sucursal.nombre}"

                serializer.validated_data["stock_previo"] = stock_previo_origen
                self.perform_create(serializer)

                # Registro dual: crear movimiento simétrico de recepción en destino
                Movimiento.objects.create(
                    tipo="Traslado",
                    id_art=producto,
                    id_suc=sucursal_destino,
                    cantidad=cantidad,
                    stock_previo=stock_previo_destino,
                    motivo=motivo_destino,
                    id_usuario=serializer.validated_data.get("id_usuario"),
                    fecha_hora=serializer.instance.fecha_hora,
                )

            if tipo in ["Entrada", "Salida"]:
                self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
