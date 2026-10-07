import re
import string
from rest_framework import serializers
from .models import Role, Usuario


def validar_password_robusta(password: str) -> None:
    """
    Valida política de contraseñas de la aplicación según lineamientos OWASP:
    - Mínimo 9 caracteres.
    - No permite espacios en blanco ni caracteres invisibles.
    - Debe incluir al menos una letra.
    - Debe incluir al menos un número.
    - Debe incluir al menos un carácter especial estándar imprimible (string.punctuation).
    """
    if not password or len(password) < 9:
        raise serializers.ValidationError(
            "La contraseña debe contener al menos 9 caracteres."
        )
    if any(c.isspace() for c in password):
        raise serializers.ValidationError(
            "La contraseña no puede contener espacios en blanco ni caracteres invisibles."
        )
    if not any(c.isalpha() for c in password):
        raise serializers.ValidationError(
            "La contraseña debe contener al menos una letra."
        )
    if not any(c.isdigit() for c in password):
        raise serializers.ValidationError(
            "La contraseña debe contener al menos un número."
        )
    if not any(c in string.punctuation for c in password):
        raise serializers.ValidationError(
            "La contraseña debe contener al menos un carácter especial válido (ej. !@#$%^&*)."
        )



class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    rol = RoleSerializer(
        read_only=True
    )  # Para mostrar los datos del rol en las respuestas
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source="rol",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Usuario  # Sin coma
        # Es mejor listar los campos para no exponer datos de seguridad internos
        fields = [
            "id",
            "email",
            "nombre",
            "dni",
            "fecha_nacimiento",
            "rol",
            "rol_id",
            "is_active",
            "is_superuser",
            "password",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },  # Hacemos que el password no sea obligatorio para poder editar usuarios sin cambiar su contraseña
            "is_superuser": {"read_only": True},  # Solo el ORM puede modificar este campo
        }

    def create(self, validated_data):
        rol_asignado = validated_data.get("rol", None)
        # Solo el Super Administrador puede crear usuarios con rol ADMINISTRADOR (ADR-0008)
        if rol_asignado and rol_asignado.nombre.upper() == "ADMINISTRADOR":
            request = self.context.get("request")
            if request and not getattr(request.user, "is_superuser", False):
                raise serializers.ValidationError(
                    {"rol_id": "Solo el Super Administrador puede asignar el rol de Administrador."}
                )

        password = validated_data.get("password")
        if password:
            validar_password_robusta(password)

        user = Usuario.objects.create_user(
            email=validated_data["email"],
            nombre=validated_data["nombre"],
            dni=validated_data["dni"],
            fecha_nacimiento=validated_data["fecha_nacimiento"],
            password=password,
            rol=rol_asignado,
        )
        return user

    def update(self, instance, validated_data):
        # Desacople de contraseñas: se ignora password en update general (ADR-0008).
        # Toda gestión de credenciales se canaliza por reset-password o me/change-password.
        validated_data.pop("password", None)

        # Solo el Super Administrador puede asignar o reasignar el rol ADMINISTRADOR
        nuevo_rol = validated_data.get("rol", None)
        if nuevo_rol and nuevo_rol.nombre.upper() == "ADMINISTRADOR":
            request = self.context.get("request")
            if request and not getattr(request.user, "is_superuser", False):
                raise serializers.ValidationError(
                    {"rol_id": "Solo el Super Administrador puede asignar el rol de Administrador."}
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer restringido para el autoservicio de perfil propio (/api/usuarios/me/).
    El usuario autenticado puede actualizar sus datos personales pero no puede
    auto-modificar campos de acceso y seguridad (rol, email, is_active, is_superuser).
    Implementa la decision del ADR-0008 (autoservicio de perfil).
    """

    rol = RoleSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "nombre",
            "dni",
            "fecha_nacimiento",
            "rol",
            "is_active",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "email",        # El email no se cambia por este endpoint
            "rol",          # Solo un admin puede cambiar el rol
            "is_active",    # Solo un admin puede activar/desactivar cuentas
            "is_superuser",
        ]


class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para el autoservicio de cambio de contraseña propia (US12 / ADR-0008).
    Requiere la clave actual y una nueva contraseña que satisfaga la política de seguridad.
    """
    password_actual = serializers.CharField(write_only=True, required=True)
    nueva_password = serializers.CharField(write_only=True, required=True)

    def validate_nueva_password(self, value):
        validar_password_robusta(value)
        return value
