from rest_framework import serializers
from .models import (
    Producto,
    Categoria,
    Sucursal,
    Proveedor,
    ProductoProveedor,
    StockSucursal,
    Movimiento,
)
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Sum


class CategoriaSerializer(serializers.ModelSerializer):
    total_articulos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ["id_cat", "nombre", "total_articulos"]

    def get_total_articulos(self, obj):
        return Producto.objects.filter(id_cat=obj).count()

    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if not nombre_limpio:
            raise serializers.ValidationError("El nombre de la categoría no puede estar vacío.")
        qs = Categoria.objects.filter(nombre__iexact=nombre_limpio)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"Ya existe una categoría con el nombre '{nombre_limpio}'."
            )
        return nombre_limpio


class ProductoProveedorSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source="id_art.nombre", read_only=True)
    nombre_proveedor = serializers.CharField(source="id_prov.nombre", read_only=True)
    cuit_proveedor = serializers.CharField(source="id_prov.cuit", read_only=True)

    class Meta:
        model = ProductoProveedor
        fields = [
            "id_enlace",
            "id_art",
            "id_prov",
            "precio_costo",
            "nombre_producto",
            "nombre_proveedor",
            "cuit_proveedor",
        ]


class ProductoSerializer(serializers.ModelSerializer):

    categoria = CategoriaSerializer(source="id_cat", read_only=True)
    nombre = serializers.CharField(allow_blank=True)
    codigo = serializers.CharField(allow_blank=True)
    stock_total = serializers.SerializerMethodField()
    proveedores = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id_art",
            "nombre",
            "descripcion",
            "codigo",
            "precio_venta",
            "stock_min_global",
            "stock_total",
            "proveedores",
            "id_cat",
            "categoria",
        ]

    def get_stock_total(self, obj):
        total = StockSucursal.objects.filter(id_art=obj).aggregate(
            total=Sum("cantidad_stock")
        )["total"]
        return total or 0

    def get_proveedores(self, obj):
        enlaces = ProductoProveedor.objects.filter(id_art=obj).select_related("id_prov")
        return [
            {
                "id_prov": e.id_prov.id_prov,
                "nombre": e.id_prov.nombre,
                "cuit": e.id_prov.cuit,
                "precio_costo": float(e.precio_costo),
            }
            for e in enlaces
        ]

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre del producto es obligatorio.")
        return value.strip()

    def validate_codigo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El código del producto es obligatorio.")

        qs = Producto.objects.filter(codigo=value.strip())
        # En edición excluimos el producto actual para no chocar consigo mismo
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"Ya existe un producto con el código '{value}'."
            )

        return value.strip()

    def validate_stock_min_global(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El stock mínimo global no puede ser negativo.")
        return value or 0


class SucursalSerializer(serializers.ModelSerializer):
    total_articulos = serializers.SerializerMethodField()
    articulos_con_stock = serializers.SerializerMethodField()
    articulos_sin_stock = serializers.SerializerMethodField()
    articulos_alerta = serializers.SerializerMethodField()

    class Meta:
        model = Sucursal
        fields = [
            "id_suc",
            "nombre",
            "direccion",
            "es_central",
            "total_articulos",
            "articulos_con_stock",
            "articulos_sin_stock",
            "articulos_alerta",
        ]

    def get_total_articulos(self, obj):
        return StockSucursal.objects.filter(id_suc=obj).count()

    def get_articulos_con_stock(self, obj):
        return StockSucursal.objects.filter(id_suc=obj, cantidad_stock__gt=0).count()

    def get_articulos_sin_stock(self, obj):
        return StockSucursal.objects.filter(id_suc=obj, cantidad_stock=0).count()

    def get_articulos_alerta(self, obj):
        return StockSucursal.objects.filter(
            id_suc=obj,
            stock_min__gt=0,
            cantidad_stock__lte=models.F("stock_min"),
        ).count()

    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if not nombre_limpio:
            raise serializers.ValidationError("El nombre de la sucursal no puede estar vacío.")
        qs = Sucursal.objects.filter(nombre__iexact=nombre_limpio)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"Ya existe una sucursal con el nombre '{nombre_limpio}'."
            )
        return nombre_limpio

    def create(self, validated_data):
        # Auto-promoción: si no existe ninguna sede central registrada, marcar automáticamente como central
        if not Sucursal.objects.filter(es_central=True).exists():
            validated_data["es_central"] = True

        es_central = validated_data.get("es_central", False)
        with transaction.atomic():
            if es_central:
                # Garantía de unicidad: desmarcar sede central previa si se define una nueva
                Sucursal.objects.filter(es_central=True).update(es_central=False)
            return super().create(validated_data)

    def update(self, instance, validated_data):
        nuevo_es_central = validated_data.get("es_central", instance.es_central)

        # Si se intenta desmarcar la única sede central sin asignar otra
        if instance.es_central and not nuevo_es_central:
            otras_centrales = Sucursal.objects.filter(es_central=True).exclude(pk=instance.pk).exists()
            if not otras_centrales:
                raise serializers.ValidationError(
                    {"es_central": "No se puede desmarcar la Casa Central sin designar previamente otra sucursal como Central."}
                )

        with transaction.atomic():
            if nuevo_es_central and not instance.es_central:
                # Al promover una sede a central, desmarcar atómicamente la anterior
                Sucursal.objects.filter(es_central=True).exclude(pk=instance.pk).update(es_central=False)
            return super().update(instance, validated_data)


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = "__all__"

    def validate_cuit(self, value):
        cuit_limpio = value.strip()
        qs = Proveedor.objects.filter(cuit__iexact=cuit_limpio)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"Ya existe un proveedor registrado con el CUIT '{cuit_limpio}'."
            )
        return cuit_limpio


class StockSucursalSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source="id_art.nombre", read_only=True)
    nombre_sucursal = serializers.CharField(source="id_suc.nombre", read_only=True)

    class Meta:
        model = StockSucursal
        fields = [
            "id_stock",
            "cantidad_stock",
            "stock_min",
            "id_art",
            "id_suc",
            "nombre_producto",
            "nombre_sucursal",
        ]
        extra_kwargs = {
            "cantidad_stock": {"read_only": True},
            "id_art": {"read_only": True},
            "id_suc": {"read_only": True},
        }


class MovimientoSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source="id_art.nombre", read_only=True)
    nombre_sucursal = serializers.CharField(source="id_suc.nombre", read_only=True)
    nombre_proveedor = serializers.CharField(
        source="id_prov.nombre", read_only=True, default=None
    )
    cuit_proveedor = serializers.CharField(
        source="id_prov.cuit", read_only=True, default=None
    )
    id_suc_destino = serializers.PrimaryKeyRelatedField(
        queryset=Sucursal.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Movimiento
        fields = "__all__"
        extra_kwargs = {
            "fecha_hora": {"required": False, "allow_null": True},
            "id_usuario": {"required": False, "allow_null": True},
            "id_prov": {"required": False, "allow_null": True},
            "id_mov": {"required": False},
        }

    def create(self, validated_data):
        validated_data.pop("id_suc_destino", None)
        if not validated_data.get("fecha_hora"):
            validated_data["fecha_hora"] = timezone.now()
        return super().create(validated_data)

