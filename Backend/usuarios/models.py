from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class Role(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre del rol (ej: Administrador, Empleado).",
    )
    descripcion = models.TextField(blank=True, help_text="Descripción del rol.")

    def __str__(self):
        return f"{self.nombre}, {self.descripcion}"


class UsuarioManager(BaseUserManager):
    def create_user(
        self, email, nombre, dni, fecha_nacimiento, password=None, **extra_fields
    ):
        if not email:
            raise ValueError(
                "El usuario debe tener un correo electrónico obligatoriamente."
            )
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nombre=nombre,
            dni=dni,
            fecha_nacimiento=fecha_nacimiento,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, nombre, dni, fecha_nacimiento, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("rol") is None:
            rol_admin, _ = Role.objects.get_or_create(
                nombre="ADMINISTRADOR",
                defaults={"descripcion": "Rol con control total del sistema"},
            )
            extra_fields["rol"] = rol_admin

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")

        return self.create_user(
            email, nombre, dni, fecha_nacimiento, password, **extra_fields
        )


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100, help_text="Nombre completo del usuario.")
    email = models.EmailField(
        unique=True, help_text="Email del usuario. Debe ser único"
    )
    dni = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r"^\d{7,8}$")],
        help_text="Número de documento, tiene que ser único y tener entre 7 u 8 dígitos.",
    )
    fecha_nacimiento = models.DateField(help_text="Fecha de nacimiento.")
    rol = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )

    # Campos requeridos por Django Auth
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    # Reemplazamos el username estándar por el email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "dni", "fecha_nacimiento"]

    def __str__(self):
        return (
            f"{self.nombre} ({self.email}), Rol: {self.rol}, Activo: {self.is_active}"
        )

    def save(self, *args, **kwargs):
        if self.is_superuser and self.rol is None:
            rol_admin, _ = Role.objects.get_or_create(
                nombre="ADMINISTRADOR",
                defaults={"descripcion": "Rol con control total del sistema"},
            )
            self.rol = rol_admin
        super().save(*args, **kwargs)

    # Lógica de roles
    @property
    def es_admin(self):
        """Devuelve True si el usuario tiene asignado el rol de Administrador o si es superusuario."""
        return self.is_superuser or (
            self.rol is not None and self.rol.nombre.lower() == "administrador"
        )

    @property
    def es_empleado(self):
        """Devuelve True si el usuario tiene asignado el rol de Empleado."""
        return self.rol is not None and self.rol.nombre.lower() in [
            "empleado",
            "ventas",
            "deposito",
        ]


class LogAuditoria(models.Model):
    EVENTOS_CHOICES = [
        ("BAJA_CUENTA", "Baja voluntaria de cuenta"),
        ("BAJA_USUARIO", "Baja administrativa de usuario"),
        ("ALTA_USUARIO", "Alta de nuevo usuario"),
        ("LOGIN_EXITOSO", "Inicio de sesión exitoso"),
        ("LOGIN_FALLIDO", "Intento de inicio de sesión fallido"),
        ("BLOQUEO_FUERZA_BRUTA", "Bloqueo por exceso de intentos"),
        ("CAMBIO_ROL", "Cambio de rol de usuario"),
        ("CAMBIO_PASSWORD", "Cambio o reseteo de contraseña"),
        ("MOVIMIENTO_STOCK", "Movimiento de stock registrado"),
    ]

    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Fecha y hora exacta en que ocurrió el evento.",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
        help_text="Usuario asociado al evento si existe en el sistema.",
    )
    usuario_email = models.CharField(
        max_length=254,
        db_index=True,
        help_text="Correo electrónico involucrado en el evento (preservado aun si el usuario se elimina o no existe).",
    )
    evento = models.CharField(
        max_length=50,
        choices=EVENTOS_CHOICES,
        db_index=True,
        help_text="Tipo de evento de seguridad auditado.",
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Detalle descriptivo o contexto del evento.",
    )
    ip_origen = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Dirección IP de origen de la solicitud HTTP.",
    )

    class Meta:
        db_table = "usuarios_log_auditoria"
        ordering = ["-fecha_hora"]
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}] {self.evento} - {self.usuario_email}"

