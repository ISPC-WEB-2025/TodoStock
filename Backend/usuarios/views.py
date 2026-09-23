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
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework.permissions import BasePermission, SAFE_METHODS


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
        # 1. Capturamos los datos que nos va a mandar Angular
        email = request.data.get("email")
        password = request.data.get(
            "password"
        )  # DRF abre json, con get extrae y guarda en variables

        # 2. Django verifica si el email y la contraseña coinciden en la base de datos
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # 3. Generamos el par de tokens JWT (Access + Refresh)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "nombre": user.nombre,
                    "access": access_token,
                    "refresh": refresh_token,
                    "token": access_token,  # Retrocompatibilidad
                    "email": user.email,
                    "es_admin": user.es_admin,
                    "es_empleado": user.es_empleado,  # booleanos para control de UI según rol
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

        # Crear el usuario
        usuario = Usuario.objects.create_user(
            nombre=nombre, email=email, dni=dni, fecha_nacimiento=fdn, password=password
        )

        return Response(
            {"mensaje": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED
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
        usuario.activo = False
        usuario.save()
        return Response(
            {"mensaje": "Usuario desactivado correctamente."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="me", permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna el perfil completo del usuario autenticado vía JWT/Token."""
        serializer = self.get_serializer(request.user)
        data = dict(serializer.data)
        data["es_admin"] = getattr(request.user, "es_admin", False)
        data["es_empleado"] = getattr(request.user, "es_empleado", False)
        return Response(data, status=status.HTTP_200_OK)
