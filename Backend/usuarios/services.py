import logging
from typing import Optional
from django.http import HttpRequest
from .models import LogAuditoria, Usuario

logger = logging.getLogger(__name__)


def obtener_ip_cliente(request: Optional[HttpRequest]) -> Optional[str]:
    """
    Obtiene la dirección IP del cliente a partir de los encabezados HTTP.
    Soporta proxies y balanceadores (HTTP_X_FORWARDED_FOR).
    """
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def registrar_auditoria(
    evento: str,
    usuario: Optional[Usuario] = None,
    email: Optional[str] = None,
    descripcion: str = "",
    request: Optional[HttpRequest] = None,
    ip: Optional[str] = None,
) -> Optional[LogAuditoria]:
    """
    Registra un evento de seguridad en la tabla LogAuditoria y en los logs del servidor.
    Diseñado para ser seguro y tolerante a fallos:
    - Desacoplado: Preserva el email aun si el usuario es None, inactivo o anónimo.
    - No bloqueante: Ante cualquier fallo al guardar, registra el error y retorna None
      sin interrumpir el flujo transaccional principal.
    """
    try:
        usuario_email = email
        user_obj = usuario

        if not usuario_email and user_obj and hasattr(user_obj, "email"):
            usuario_email = user_obj.email

        if not usuario_email and request and hasattr(request, "user") and request.user.is_authenticated:
            usuario_email = getattr(request.user, "email", "")
            if not user_obj:
                user_obj = request.user

        if not usuario_email:
            usuario_email = "anonimo@sistema.local"

        ip_origen = ip
        if not ip_origen and request:
            ip_origen = obtener_ip_cliente(request)

        # Solo asociamos ForeignKey si es un Usuario persistido en BD
        user_fk = user_obj if (user_obj and hasattr(user_obj, "pk") and user_obj.pk) else None

        log_entry = LogAuditoria.objects.create(
            usuario=user_fk,
            usuario_email=usuario_email,
            evento=evento,
            descripcion=descripcion,
            ip_origen=ip_origen,
        )

        logger.info(
            "[AUDITORIA] %s | Usuario: %s | IP: %s | Detalle: %s",
            evento,
            usuario_email,
            ip_origen or "N/A",
            descripcion,
        )
        return log_entry
    except Exception as e:
        logger.exception("[AUDITORIA ERROR] Fallo al asentar log de auditoría: %s", str(e))
        return None
