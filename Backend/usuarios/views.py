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
from rest_framework.throttling import AnonRateThrottle
from rest_framework import serializers
from django.db import IntegrityError
from .models import Usuario, Role, LogAuditoria
from .serializers import (
    UsuarioSerializer,
    PerfilUsuarioSerializer,
    RoleSerializer,
    CambiarPasswordSerializer,
    RegistroUsuarioSerializer,
    LogAuditoriaSerializer,
    validar_password_robusta,
)
from .services import registrar_auditoria
from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


class EsAdministrador(BasePermission):
    """
    Permite acceso únicamente a usuarios autenticados con rol Administrador o Superusuario.
    Aplica tanto a métodos de lectura (GET) como de escritura (TK51).
    """
    message = "Acceso exclusivo para el Administrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, "es_admin", False) or getattr(request.user, "is_superuser", False))
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EsAdminParaModificar(BasePermission):
    """
    Permite a cualquier usuario logueado VER (GET - safe methods).
    Requiere ser Administrador o Superusuario para CREAR, EDITAR o BORRAR.
    Aplica jerarquía estricta (ADR-0008):
    - Únicamente el Super Administrador puede editar, desactivar o resetear a otros Administradores o Superusuarios.
    - Se prohíbe desactivar al Super Administrador principal.
    """
    message = "Acción reservada al Administrador."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, "es_admin", False) or getattr(request.user, "is_superuser", False))
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        # Si el objeto inspeccionado es un Usuario
        if isinstance(obj, Usuario):
            # Nadie puede desactivar al superusuario raíz
            if obj.is_superuser and request.method == "DELETE":
                self.message = "No se puede desactivar la cuenta del Super Administrador principal."
                return False

            # Si el target es Administrador o Superusuario distinto a uno mismo, solo el Super Administrador puede operar sobre él
            target_es_admin = getattr(obj, "es_admin", False) or getattr(obj, "is_superuser", False)
            if target_es_admin and obj != request.user and not getattr(request.user, "is_superuser", False):
                self.message = "Acción reservada al Super Administrador."
                return False

        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, "es_admin", False) or getattr(request.user, "is_superuser", False))
        )


class EsAdminPadronUsuarios(BasePermission):
    """
    Blindaje de padrón de usuarios (US14 / RNF-SEG):
    - Únicamente los Administradores pueden listar o consultar el padrón de usuarios (GET).
    - Aplica jerarquía estricta (ADR-0008) sobre operaciones de modificación y desactivación.
    - Protege datos personales de empleados contra accesos de operadores sin privilegios.
    """
    message = "Acceso exclusivo para el Administrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, "es_admin", False) or getattr(request.user, "is_superuser", False))
        )

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False

        if isinstance(obj, Usuario):
            # Nadie puede desactivar al superusuario raíz
            if obj.is_superuser and request.method == "DELETE":
                self.message = "No se puede desactivar la cuenta del Super Administrador principal."
                return False

            # Si el target es Administrador o Superusuario distinto a uno mismo, solo el Super Administrador puede operar sobre él
            target_es_admin = getattr(obj, "es_admin", False) or getattr(obj, "is_superuser", False)
            if target_es_admin and obj != request.user and not getattr(request.user, "is_superuser", False):
                self.message = "Acción reservada al Super Administrador."
                return False

        return True



class LoginUsuarioView(APIView):
    throttle_classes = [AnonRateThrottle]  # TK46: límite de intentos de login
    permission_classes = [AllowAny]
    authentication_classes = []

    def throttled(self, request, wait):
        """
        Sobrescribe el manejador de rate limit de DRF (TK46 / TK58).
        Registra el bloqueo temporal por fuerza bruta en LogAuditoria antes de lanzar HTTP 429.
        """
        email_intento = None
        if hasattr(request, "data") and isinstance(getattr(request, "data"), dict):
            email_intento = request.data.get("email")
        elif hasattr(request, "POST") and request.POST.get("email"):
            email_intento = request.POST.get("email")
        elif hasattr(request, "body") and request.body:
            try:
                import json
                body_decoded = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
                parsed = json.loads(body_decoded)
                if isinstance(parsed, dict):
                    email_intento = parsed.get("email")
            except Exception:
                pass

        registrar_auditoria(
            evento="BLOQUEO_FUERZA_BRUTA",
            email=email_intento or "desconocido",
            descripcion=f"Login bloqueado temporalmente por exceso de intentos (fuerza bruta). Tiempo de espera requerido: {wait} segundos.",
            request=request,
        )
        super().throttled(request, wait)

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
                registrar_auditoria(
                    evento="LOGIN_FALLIDO",
                    usuario=user,
                    email=user.email,
                    descripcion="Intento de acceso rechazado: cuenta inactiva o pendiente de aprobación.",
                    request=request,
                )
                return Response(
                    {"error": "Cuenta pendiente de aprobación por el administrador."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # 4. Generamos el par de tokens JWT (Access + Refresh)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            registrar_auditoria(
                evento="LOGIN_EXITOSO",
                usuario=user,
                email=user.email,
                descripcion="Inicio de sesión exitoso.",
                request=request,
            )

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
                    "is_superuser": user.is_superuser,
                },
                status=status.HTTP_200_OK,
            )
        else:
            registrar_auditoria(
                evento="LOGIN_FALLIDO",
                email=email or "desconocido",
                descripcion="Intento de inicio de sesión fallido con credenciales inválidas.",
                request=request,
            )
            return Response(
                {"error": "Email o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RegistroUsuarioView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin hacer login
    authentication_classes = []

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if not serializer.is_valid():
            # Extraer primer error de detalle si está disponible para mensaje legible
            first_error_msg = None
            for field, errors in serializer.errors.items():
                if isinstance(errors, list) and len(errors) > 0:
                    first_error_msg = f"{field}: {errors[0]}" if field != "non_field_errors" else str(errors[0])
                    break
                elif isinstance(errors, str):
                    first_error_msg = errors
                    break

            return Response(
                {
                    "error": first_error_msg or "Datos de registro inválidos.",
                    "detalles": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            nuevo_usuario = serializer.save()
            registrar_auditoria(
                evento="ALTA_USUARIO",
                usuario=nuevo_usuario,
                email=nuevo_usuario.email,
                descripcion="Nuevo usuario registrado (cuenta inactiva pendiente de aprobación).",
                request=request,
            )
        except IntegrityError:
            return Response(
                {"error": "El DNI o email ya se encuentra registrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"mensaje": "Cuenta creada. Aguardá la aprobación del administrador para poder ingresar."},
            status=status.HTTP_201_CREATED,
        )



# --- VISTA DEL CRUD DE USUARIOS (TK58 / ADR-0008 / US14) ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [
        EsAdminPadronUsuarios
    ]  # Solo los administradores pueden listar y gestionar el padrón de usuarios (US14/RNF-SEG)

    def perform_update(self, serializer):
        usuario_previo = self.get_object()
        rol_previo = usuario_previo.rol.nombre if usuario_previo.rol else "Sin rol"
        activo_previo = usuario_previo.is_active

        instancia = serializer.save()

        rol_nuevo = instancia.rol.nombre if instancia.rol else "Sin rol"
        activo_nuevo = instancia.is_active

        if rol_previo != rol_nuevo:
            registrar_auditoria(
                evento="CAMBIO_ROL",
                usuario=instancia,
                email=instancia.email,
                descripcion=f"Rol modificado de '{rol_previo}' a '{rol_nuevo}' por {self.request.user.email}.",
                request=self.request,
            )

        if not activo_previo and activo_nuevo:
            registrar_auditoria(
                evento="ALTA_USUARIO",
                usuario=instancia,
                email=instancia.email,
                descripcion=f"Cuenta activada/aprobada por {self.request.user.email}.",
                request=self.request,
            )

    # Sobreescribimos solo destroy para no borrar sino desactivar
    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        usuario.is_active = False
        usuario.save()
        registrar_auditoria(
            evento="BAJA_USUARIO",
            usuario=usuario,
            email=usuario.email,
            descripcion=f"Usuario desactivado administrativamente por {request.user.email}.",
            request=request,
        )
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
        Implementa ADR-0008 (autoservicio de perfil) y asienta evento en LogAuditoria (TK51/TK59).
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
            if getattr(request.user, "is_superuser", False):
                return Response(
                    {"error": "No se puede desactivar la cuenta del Super Administrador principal."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user_a_desactivar = request.user
            user_email = user_a_desactivar.email
            user_a_desactivar.is_active = False
            user_a_desactivar.save()

            registrar_auditoria(
                evento="BAJA_CUENTA",
                usuario=user_a_desactivar,
                email=user_email,
                descripcion=f"Baja voluntaria de cuenta solicitada por el propio usuario ({user_email}).",
                request=request,
            )

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

        registrar_auditoria(
            evento="CAMBIO_PASSWORD",
            usuario=request.user,
            email=request.user.email,
            descripcion="El usuario actualizó exitosamente su propia contraseña.",
            request=request,
        )

        return Response(
            {"mensaje": "Contraseña actualizada exitosamente."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reset-password",
        permission_classes=[EsAdminParaModificar],
    )
    def reset_password(self, request, pk=None):
        """
        POST /api/usuarios/<id>/reset-password/
        Reseteo administrativo de contraseña (ADR-0008 / #US08).
        Un Administrador estándar solo puede resetear contraseñas de cuentas operativas.
        El reseteo de cuentas ADMINISTRADOR o Superusuario está reservado al Super Administrador.
        """
        usuario = self.get_object()
        if usuario == request.user:
            return Response(
                {
                    "error": "No puedes usar el reseteo administrativo sobre tu propia cuenta. Utiliza 'Mi Perfil' para cambiar tu contraseña ingresando la clave actual."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        nueva_password = request.data.get("nueva_password") or request.data.get("password")
        if not nueva_password:
            return Response(
                {"error": "El campo 'nueva_password' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validar_password_robusta(nueva_password)
        except serializers.ValidationError as e:
            msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        usuario.set_password(nueva_password)
        usuario.save()

        registrar_auditoria(
            evento="CAMBIO_PASSWORD",
            usuario=usuario,
            email=usuario.email,
            descripcion=f"Contraseña restablecida administrativamente por {request.user.email}.",
            request=request,
        )

        return Response(
            {"mensaje": f"Contraseña del usuario '{usuario.email}' restablecida exitosamente."},
            status=status.HTTP_200_OK,
        )


# --- AUDITORÍA DE SEGURIDAD (TK51 / US14) ---
class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/usuarios/auditoria/ — Consulta de eventos de seguridad y trazabilidad.
    Solo lectura. Acceso estrictamente reservado a administradores (EsAdministrador).
    """
    queryset = LogAuditoria.objects.all().order_by("-fecha_hora")
    serializer_class = LogAuditoriaSerializer
    permission_classes = [EsAdministrador]



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
    authentication_classes = []

    def post(self, request):
        email = (request.data.get("email") or getattr(request.user, "email", "")).strip()
        asunto = request.data.get("asunto", "").strip()
        mensaje = request.data.get("mensaje", "").strip()

        if not email:
            return Response(
                {"error": "El correo electrónico de contacto es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not asunto or not mensaje:
            return Response(
                {"error": "Los campos 'asunto' y 'mensaje' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "[SOPORTE] De: %s | Asunto: %s | Mensaje: %s",
            email, asunto, mensaje,
        )
        print(
            f"\n📨 [SOPORTE RECIBIDO]\n   De: {email}\n   Asunto: {asunto}\n   Mensaje: {mensaje}\n",
            flush=True,
        )

        return Response(
            {"mensaje": "Consulta recibida. Nos pondremos en contacto a la brevedad."},
            status=status.HTTP_200_OK,
        )
