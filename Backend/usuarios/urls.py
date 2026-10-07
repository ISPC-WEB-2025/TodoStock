from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginUsuarioView, RegistroUsuarioView, UserViewSet, RoleViewSet, ContactoSoporteView

# 1. Registramos los viewsets en el router
router = DefaultRouter()
# IMPORTANTE: 'roles' se registra primero para que el DefaultRouter no lo confunda
# con el pk de un usuario en la ruta raiz '' (ej: /api/usuarios/roles/ vs /api/usuarios/<pk>/)
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'', UserViewSet, basename='usuario')

urlpatterns = [
    # 2. La ruta de login
    path('login/', LoginUsuarioView.as_view(), name='api_login'),
    # 3. La ruta de refresco de tokens JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 4. La ruta de registro (crea cuenta con is_active=False, pendiente de aprobacion)
    path('registro/', RegistroUsuarioView.as_view(), name='api_registro'),
    # 5. Formulario de contacto y soporte (US04 — sin SMTP, registra en log del servidor)
    path('contacto/', ContactoSoporteView.as_view(), name='api_contacto'),
    # 6. Rutas del router: CRUD de usuarios + /roles/ + /me/ (autoservicio de perfil)
    path('', include(router.urls)),
]