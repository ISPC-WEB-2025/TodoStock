import logging

from rest_framework.views import APIView
from rest_framework.response import (
    Response,
)  # Es el traductor. Agarra diccionarios de Python y los convierte en JSON
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import (
    status,
)  # Nos da códigos de estado HTTP para usar en las respuestas (200, 400, 401, etc)
from django.contrib.auth import (
    authenticate,
)  # va a la base de datos, busca el usuario y verifica si la contraseña desencriptada coincide.

# from django.contrib.auth.models import (User, Group)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from .models import Usuario, Role
from .serializers import (
    UsuarioSerializer,
    PerfilUsuarioSerializer,
    RoleSerializer,
    CambiarPasswordSerializer,
    validar_password_robusta,
)
from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


class EsAdminParaModificar(BasePermission):
    # Permite a cualquier usuario logueado VER (GET),
    # pero solo a los Administradores CREAR, EDITAR o BORRAR.

    def has_permission(self, request, view):
        # Si la petición es GET (solo lectura - SAFE_METHODS), dejamos pasar
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Si es POST, PUT o DELETE, verificamos que sea admin usando tu propiedad 'es_admin'
        return bool(
            request.user and request.user.is_authenticated and request.user.es_admin
        )


class LoginUsuarioView(APIView):
    permission_classes = [AllowAny]

    def post(
        self, request
    ):  # define vista, solo recibe post, no get (ej barra de naveg) / request contiene lo que envía Angular
        # 1. Capturamos los datos que nos va a mandar el cliente
        email = request.data.get("email")
        password = request.data.get(
            "password"
        )  # DRF abre json, con get extrae y guarda en variables

        # 2. Django verifica si el email y la contraseña coinciden en la base de datos
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # 3. Guardia: si la cuenta existe pero está inactiva (pendiente de aprobación)
            if not user.is_active:
                return Response(
                    {"error": "Cuenta pendiente de aprobación por el administrador."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # 4. Generamos el par de tokens JWT (Access + Refresh)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "id": user.id,              # ID del usuario para la app mobile
                    "nombre": user.nombre,
                    "access": access_token,
                    "refresh": refresh_token,
                    "token": access_token,  # Retrocompatibilidad con el cliente web Angular
                    "email": user.email,
                    "es_admin": user.es_admin,
                    "es_empleado": user.es_empleado,  # booleanos para control de UI según rol (ADR-0007)
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Email o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RegistroUsuarioView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin hacer login

    def post(self, request):
        nombre = request.data.get("nombre")
        email = request.data.get("email")
        dni = request.data.get("dni")
        fdn = request.data.get("fdn")
        password = request.data.get("password")

        # Validaciones
        if not nombre or not email or not password:
            return Response(
                {"error": "Falta datos de nombre, email o contraseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Usuario.objects.filter(email=email).exists():
            return Response(
                {"error": "Este email ya existe."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validar política de contraseña robusta (US07, TK47)
        try:
            validar_password_robusta(password)
        except serializers.ValidationError as e:
            msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario como inactivo — requiere aprobación del administrador (US07)
        Usuario.objects.create_user(
            nombre=nombre, email=email, dni=dni, fecha_nacimiento=fdn,
            password=password, is_active=False,
        )

        return Response(
            {"mensaje": "Cuenta creada. Aguardá la aprobación del administrador para poder ingresar."},
            status=status.HTTP_201_CREATED,
        )


# --- VISTA DEL CRUD DE USUARIOS (TK58) ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [
        EsAdminParaModificar
    ]  # Solo los admins pueden modificar, pero todos los usuarios logueados pueden ver la lista de usuarios

    # Sobreescribimos solo destroy para no borrar sino desactivar
    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        usuario.is_active = False
        usuario.save()
        return Response(
            {"mensaje": "Usuario desactivado correctamente."}, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["get", "patch", "delete"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """
        GET  — Retorna el perfil completo del usuario autenticado.
        PATCH — Actualiza datos personales propios (nombre, dni, fecha_nacimiento).
                Campos sensibles (rol, email, is_active, is_superuser) son ignorados.
        DELETE — Desactiva la cuenta propia (is_active=False). No borra el registro.
        Implementa ADR-0008 (autoservicio de perfil).
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            data = dict(serializer.data)
            data["es_admin"] = getattr(request.user, "es_admin", False)
            data["es_empleado"] = getattr(request.user, "es_empleado", False)
            return Response(data, status=status.HTTP_200_OK)

        elif request.method == "PATCH":
            serializer = PerfilUsuarioSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            request.user.is_active = False
            request.user.save()
            return Response(
                {"mensaje": "Cuenta desactivada. El administrador puede reactivarla cuando lo solicites."},
                status=status.HTTP_200_OK,
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-password",
        permission_classes=[IsAuthenticated],
    )
    def change_password(self, request):
        """
        POST /api/usuarios/me/change-password/
        Permite al usuario autenticado cambiar su propia contraseña.
        Requiere password_actual y nueva_password (mínimo 9 caracteres, letras, números y símbolos).
        Implementa US12 / ADR-0008.
        """
        serializer = CambiarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_actual = serializer.validated_data["password_actual"]
        nueva_password = serializer.validated_data["nueva_password"]

        if not request.user.check_password(password_actual):
            return Response(
                {"error": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password_actual == nueva_password:
            return Response(
                {"error": "La nueva contraseña no puede ser idéntica a la contraseña actual."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(nueva_password)
        request.user.save()

        return Response(
            {"mensaje": "Contraseña actualizada exitosamente."},
            status=status.HTTP_200_OK,
        )


# --- ROLES (solo lectura — para selectores en la app mobile) ---
class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/usuarios/roles/ — Lista los roles disponibles del sistema.
    Usado por la app mobile para poblar selectores de asignación de rol en la
    gestión de usuarios (US08). Solo lectura; la creación de roles es exclusiva del ORM/admin.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


# --- CONTACTO Y SOPORTE (US04) ---
class ContactoSoporteView(APIView):
    """
    POST /api/usuarios/contacto/ — Recibe consultas de soporte desde la app mobile.
    No requiere tabla adicional: la consulta se registra en el log del servidor.
    No requiere configuracion SMTP; homogeneo con el resto de la API REST (Retrofit en Android).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email") or getattr(request.user, "email", "anonimo")
        asunto = request.data.get("asunto", "").strip()
        mensaje = request.data.get("mensaje", "").strip()

        if not asunto or not mensaje:
            return Response(
                {"error": "Los campos 'asunto' y 'mensaje' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "[SOPORTE] De: %s | Asunto: %s | Mensaje: %s",
            email, asunto, mensaje,
        )

        return Response(
            {"mensaje": "Consulta recibida. Nos pondremos en contacto a la brevedad."},
            status=status.HTTP_200_OK,
        )
