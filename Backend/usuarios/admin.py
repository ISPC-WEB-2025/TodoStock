from django.contrib import admin
from .models import Role, Usuario, LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha_hora", "evento", "usuario_email", "ip_origen", "descripcion_corta")
    list_filter = ("evento", "fecha_hora")
    search_fields = ("usuario_email", "descripcion", "ip_origen")
    readonly_fields = ("fecha_hora", "usuario", "usuario_email", "evento", "descripcion", "ip_origen")
    ordering = ("-fecha_hora",)

    def descripcion_corta(self, obj):
        if obj.descripcion and len(obj.descripcion) > 60:
            return obj.descripcion[:57] + "..."
        return obj.descripcion or "-"
    descripcion_corta.short_description = "Detalle"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Usuario)
admin.site.register(Role)