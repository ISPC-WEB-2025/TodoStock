from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


class Categoria(models.Model):
    id_cat = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False  # Evita que Django intente crear la tabla (que solo lea, ya las creamos)
        db_table = "CATEGORIA"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_art = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True)
    precio_venta = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    stock_min_global = models.IntegerField(default=0)
    id_cat = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column="id_cat")
    # Agregamos db_column='id_cat' para que busque la columna exacta que creaste
    # sin db_column='id_cat', django agrega _id al final del nombre (despues no coincide con la BD)

    class Meta:
        managed = False  # Le dice a Django que no intente modificar ni crear la tabla, que lea las que ya están creadas manualmente
        db_table = "PRODUCTO"

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    id_suc = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=300)
    es_central = models.BooleanField(default=False, db_column="es_central")

    class Meta:
        managed = False
        db_table = "SUCURSAL"

    def __str__(self):
        return f"{self.nombre}{' (Central)' if self.es_central else ''}"


class Proveedor(models.Model):
    id_prov = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    cuit = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=30)
    email = models.CharField(max_length=150)
    direccion = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = "PROVEEDOR"

    def __str__(self):
        return self.nombre


class ProductoProveedor(models.Model):
    id_enlace = models.AutoField(primary_key=True)
    id_art = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column="id_art",
        related_name="proveedores_enlace",
    )
    id_prov = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column="id_prov",
        related_name="productos_enlace",
    )
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = "PRODUCTO_PROVEEDOR"

    def __str__(self):
        return f"{self.id_art.nombre} - {self.id_prov.nombre}"


class StockSucursal(models.Model):
    id_stock = models.AutoField(primary_key=True)
    cantidad_stock = models.IntegerField(default=0)
    stock_min = models.IntegerField(default=0)
    id_art = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_art")
    id_suc = models.ForeignKey(Sucursal, on_delete=models.PROTECT, db_column="id_suc")

    class Meta:
        managed = False
        db_table = "STOCK_SUCURSAL"


class Movimiento(models.Model):
    TIPO_CHOICES = [
        ("Entrada", "Entrada"),
        ("Salida", "Salida"),
        ("Traslado", "Traslado"),
    ]

    id_mov = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_hora = models.DateTimeField()
    stock_previo = models.IntegerField(null=True, blank=True)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=255, null=True, blank=True)

    # Referenciamos de este mismo archivo
    id_art = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_art")
    id_suc = models.ForeignKey(Sucursal, on_delete=models.PROTECT, db_column="id_suc")
    id_prov = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, db_column="id_prov", null=True, blank=True
    )

    # Usuario está en otra aplicación (usuarios/models.py)
    # Por eso lo mantenemos entre comillas, para que Django lo vaya a buscar allá (no requiere importarlo acá, lo busca al momento de ejecutar la migración)
    # Lazy-loading: para evitar problemas de importación circular si dsp necesitamos importar algo de acá en usuarios/models.py
    id_usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        db_column="id_usuario",
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "MOVIMIENTO"

    def __str__(self):
        return f"{self.tipo} - {self.cantidad} unid. de {self.id_art.nombre} ({self.fecha_hora.strftime('%d/%m/%Y')})"


@receiver(post_save, sender=Producto)
def auto_inicializar_stock_producto(sender, instance, created, **kwargs):
    if created:
        sucursales = Sucursal.objects.all()
        for suc in sucursales:
            StockSucursal.objects.get_or_create(
                id_art=instance,
                id_suc=suc,
                defaults={"cantidad_stock": 0, "stock_min": 0},
            )


@receiver(post_save, sender=Sucursal)
def auto_inicializar_stock_sucursal(sender, instance, created, **kwargs):
    if created:
        productos = Producto.objects.all()
        for prod in productos:
            StockSucursal.objects.get_or_create(
                id_art=prod,
                id_suc=instance,
                defaults={"cantidad_stock": 0, "stock_min": 0},
            )

